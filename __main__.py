from relative import (MAIN, PROMPT, Tag, ask, call, check_path, configure,
                      driver, ec, end, exists, get_compiler, get_filter,
                      get_html, get_js, get_path, mkdir_if_not_exists, parent,
                      set_path)


#  Formats results [0-9] for selection
def show_list(titlelist):
    return (lambda MAX: 'Search results from "{0}"\n\n{2}\n{1}\n{2}'.format(search, "\n".join(("%s%s[%i]" % (t, " " * (MAX - len(t)), i) for i, t in enumerate(titlelist))), "-" * (MAX  + 3))) (len(max(titlelist, key=len)) + 5)

#  Create dictionary for data
def show_dict(data):
    return {str(i): th for i, th in enumerate(data)}


#  Prompt user with results and grab title and href based from input
def list_search(soup):

    if soup.find("ul", class_="anime-list").find("li"):
        return (lambda data: show_dict(data).get(ask(show_list([t[0] for t in data])))) ([(a["data-jtitle"], a["href"][1:]) for a in [li.find("a", class_="name") for li in soup.find("ul", class_="anime-list").find_all("li")[:10]]])
    else:
        end("Anime not found")


#  Selects applicable episode(s) for download
def sort_input(inp):

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
def grab_episodes(driver):
    for ul in list(get_js(driver, episode_url.rsplit("/", 1)[0], ec("//ul[@class='episodes']")))[0].find_all("ul", class_="episodes"):
        for li in ul:
            for a in li:
                if isinstance(a, Tag):
                    yield a["data-base"]


#  Search anime or configure downloader
def main(dl_path):

    if not dl_path or not check_path(dl_path):
        set_path()
        return main(get_path())

    inp = ask(PROMPT % dl_path, True)

    if inp.startswith("/"):
        configure(inp[1:])
        return main(get_path())

    return inp, dl_path


#  Anime requested by the user along with download path
search, path = main(get_path())


# Grabs title and server of anime specified
anime, href = list_search(get_html(MAIN + get_filter() + search.replace(" ", "+")))


#  Format episode url according to href of anime
episode_url = MAIN + href + "/ep-%s"


#  Creates new tree if directory of anime title does not exist
path += f"/{anime.replace('/', '-')}/Episode %s.mp4"


#  Grabs each valid episode
print("Grabbing available episodes...")
eps = list(grab_episodes(driver()))


#  Grabs episodes from EPS list according to user input
requested = sort_input(ask(f"Which Episodes ({eps[0]}-{eps[-1]}):", True))


#  Create new directory if path is non-existant
mkdir_if_not_exists(path.rsplit("/", 1)[0])


#  Sort data and begin download(s) as a new process
if call('%s %sbackground.py %s %s %s >/dev/null 2>%serror.out &' % (get_compiler(), parent, "".join((lambda filt: [filt.get(char) if char in filt.keys() else char for char in path]) ({" ": "_", "(": "\\(", ")": "\\)"})), episode_url, " ".join(requested), parent)) == 0:
    end((lambda l: f"Downloading {l} episode{'s' if l > 1 else ''} in the background") (len(requested)), False)
else:
    end("Error occured when beginning download", False)
