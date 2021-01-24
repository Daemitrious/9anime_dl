from relative import (MAIN, PROMPT, Popen, Tag, ask, change_path, config,
                      driver, ec, end, exists, get, gethtml, getjs,
                      mkdir_if_not_exists, parent, post, readconfig)


#  Formats results [0-9] for selection
def show_list(titlelist):
    return (lambda MAX: 'Search results from "{0}"\n\n{2}\n{1}\n{2}'.format(search, "\n".join(("%s%s[%i]" % (t, " " * (MAX - len(t)), i) for i, t in enumerate(titlelist))), "-" * (MAX  + 3))) (len(max(titlelist, key=len)) + 5)

#  Create dictionary for data
def show_dict(data):
    return {str(i): th for i, th in enumerate(data)}


#  Prompt user with results and grab title and href based from input
def listsearch(soup):

    if soup.find("ul", class_="anime-list").find("li"):
        return (lambda data: show_dict(data).get(ask(show_list([t[0] for t in data])))) ([(a["data-jtitle"], a["href"][1:]) for a in [li.find("a", class_="name") for li in soup.find("ul", class_="anime-list").find_all("li")[:10]]])
    else:
        end("Anime not found")


#  Selects applicable episode(s) for download
def sortinput(inp):

    try:
        if "-" not in inp:
            if not exists(path % inp):
                return [eps[eps.index(inp)]]
            else:
                end("Episode already downloaded")

        else:
            return [ep for ep in eps[(lambda start, end: slice(start, end + 1)) (*(eps.index(indice) for indice in inp.split("-")))] if not exists(path % ep)]

    except IndexError:
        end("Invalid Episode")


#  Grab each episode number from each ul available
def grabeps(driver):
    for ul in list(getjs(driver, epurl.rsplit("/", 1)[0], ec("//ul[@class='episodes']")))[0].find_all("ul", class_="episodes"):
        for li in ul:
            for a in li:
                if isinstance(a, Tag):
                    yield a["data-base"]


#  Search anime or configure downloader
def main():
    path = readconfig()

    if not exists(path):
        change_path()
        main()
    else:
        inp = ask(PROMPT % path, True)

    if inp.startswith("/"):
        config(inp[1:])
        main()
    else:
        return inp, path


#  Anime requested by the user along with download path
search, path = main()


# Grabs title and server of anime specified
anime, href = listsearch(gethtml(MAIN + "search?keyword=" + search.replace(" ", "+")))


#  Format episode url according to href of anime
epurl = MAIN + href + "/ep-%s"


#  Creates new tree if directory of anime title does not exist
path += f"/{anime.replace('/', '-')}/Episode %s.mp4"


#  Grabs each valid episode
print("Grabbing available episodes...")
eps = list(grabeps(driver()))


#  Grabs episodes from EPS list according to user input
requested = sortinput(ask(f"Which Episodes ({eps[0]}-{eps[-1]}):", True))


#  Create new directory if path is non-existant
mkdir_if_not_exists(path.rsplit("/", 1)[0])



#  Sort data and begin download(s) in under a new service
if Popen([f"nohup python3.8 {parent}background.py {path} {epurl} {' '.join(requested)} >/dev/null &"], shell=True).wait() == 0:
    end((lambda l: f"Downloading {l} episode{'s' if l > 1 else ''} in the background") (len(requested)), False)
else:
    end("Error occured when beginning download", False)
