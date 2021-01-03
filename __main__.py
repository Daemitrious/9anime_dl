from selenium.common.exceptions import TimeoutException

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from subprocess import Popen

from requests import get, post
from bs4 import BeautifulSoup, Tag

from os import makedirs
from os.path import exists

from getpass import getuser



#  Main Host  |  https://www12.9anime.to
#  Data Host  |  https://vidstream.pro



def clear():  #  For formatting purposes
    Popen("cls", shell=True).wait()


def kill(reason):  #  In case of uncaught exception
    exit(ask(f"Press Enter to exit  |  [{reason}]", True))


def status(content, static=False, bag=['']):  #  Print over initial print

    if static:
        print(" " * len(bag[-1]) + "\r" + content)
    else:
        content += "..."
        bag.append(content)
        print(content + " " * len(bag[-2]), end="\r")


def ask(content, before=False):  #  Formatted for user-input

    if before:
        clear()

    output = input(content + "\n\n\t> ")

    clear()

    return output


def headless(options):  #  Set Options (selenium) to headless mode
    options.add_argument("--headless")
    return options

def driver():  #  Initiate selenium.webdriver
    return Firefox(options=headless(Options()))


def ec(xpath):  #  Premade EC for WebDriverWait
    return expected_conditions.visibility_of_element_located((By.XPATH, xpath))


def mkdir_if_not_exists(path):  #  Make directory if "path" doesn't exist
    if not exists(path):
        makedirs(path)


def soupify(html):  #  html  ->  BeautifulSoup
    return BeautifulSoup(html, "lxml")


def gethtml(url):  #  requests.get
    return soupify(get(url).text)

def getjs(Driver, urls, find):  #  Driver.get
    Wait = WebDriverWait(Driver, 5, 3)

    for url in (urls if isinstance(urls, list) else [urls]):
        while True:
            try:
                Driver.get(url)

                Wait.until(find)

                yield soupify(Driver.page_source)

            except TimeoutException:
                continue

            break

    Driver.quit()


def show_list(titlelist):  #  Formats results [0-9] for selection
    return (lambda MAX: 'Search results from "{0}"\n\n{2}\n{1}\n{2}'.format(search, "\n".join(("%s%s[%i]" % (t, " " * (MAX - len(t)), i) for i, t in enumerate(titlelist))), "-" * (MAX  + 3))) (len(max(titlelist, key=len)) + 5)

def show_dict(data):  #  Create dictionary for data
    return {str(i): th for i, th in enumerate(data)}


def listsearch(soup):  #  Prompt user with results of search and grab title and href based off input
    if soup.find("ul", class_="anime-list").find("li"):
        return (lambda data: show_dict(data).get(ask(show_list([t[0] for t in data])))) ([(a["data-jtitle"], a["href"][1:]) for a in [li.find("a", class_="name") for li in soup.find("ul", class_="anime-list").find_all("li")[:10]]])
    else:
        kill("Anime not found")


def sortinput(inp):  #  Selects applicable episode(s) for download

    try:
        if "-" not in inp:
            if not exists(path % inp):
                return [eps[eps.index(inp)]]
            else:
                kill("Episode already downloaded")

        else:
            return [ep for ep in eps[(lambda start, end: slice(start, end + 1)) (*(eps.index(indice) for indice in inp.split("-")))] if not exists(path % ep)]

    except IndexError:
        kill("Invalid Episode")


def grabeps(driver):  #  Grab each episode number from each ul available
    for ul in list(getjs(driver, epURL.rsplit("/", 1)[0], ec("//ul[@class='episodes']")))[0].find_all("ul", class_="episodes"):
        for li in ul:
            for a in li:
                if isinstance(a, Tag):  #  Might need Try/Except (ValueError)
                    yield a["data-base"]

def grabkey(soup):  #  Grabs key for specified episode
    return soup.find("div", id="player").find("iframe")["src"].split("?")[0].rsplit("/", 1)[1]

def grabdl(URL):  #  Post request in order to grab downlink link from direct host
    return post(URL, data={"token": gethtml(URL).find("input", type="hidden")["value"]}, headers={"Content-Type": "application/x-www-form-urlencoded"}, stream=True).url


def grabbing(driver, EPISODES):  #  Grabs path and direct download link for each episode
    return [(p[:-4].rsplit("\\", 1)[1], p, dl) for p, dl in zip([path % ep for ep in EPISODES], [grabdl(VIDSTREAM + grabkey(soup)) for soup in getjs(driver, [epURL % ep for ep in EPISODES], ec("//div[@id='player']//iframe"))])]


def download(info):  #  Writes the content of each direct download link to the specified path.
    for ep, p, url in info:
        with open(p, "wb") as f:
            status("Downloading " + ep)

            for chunk in get(url, stream=True).iter_content(1024):
                f.write(chunk)

            status("Downloaded: " + ep, True)



MAIN = "https://www12.9anime.to/"
VIDSTREAM = "https://vidstream.pro/download/"


path = "C:\\Users\\" + getuser() + "\\Videos\\Anime"


FILTER = {"\\":"-", "/":"-", ":":" -", "*":"", "?":"" , '"':"'", "<":"-", ">":"-", "|": "-"}


#  Anime requested by the user
search = ask(f'Download Path:  "{path}"', True)


# Grabs title and server of anime specified
status("Locating")
anime, href = listsearch(gethtml(MAIN + "search?keyword=" + search.replace(" ", "+")))


#  Format episode url according to href of anime
status("Found")
epURL = MAIN + href + "/ep-%s"


#  Creates new tree if directory of anime title does not exist
path += f"\\{''.join(map(lambda char: FILTER.get(char) if char in FILTER.keys() else char, anime))}\\Episode %s.mp4"


#  Grabs each valid episode
status("Grabbing episodes")
eps = list(grabeps(driver()))


#  Grabs episodes from EPS list according to user input
requested = sortinput(ask(f"Which Episodes ({eps[0]}-{eps[-1]}):"))


#  For formatting purposes
plural, amount = "s" if len(requested) > 1 else '', len(requested)


#  Grabs direct download from host if applicable episode
status(f"Requesting direct link{plural} from host")
info = grabbing(driver(), requested)


#  Create new directory if path is non-existant
mkdir_if_not_exists(path.rsplit("\\", 1)[0])


#  Downloads each episode to according path
status(f'Requested {amount} episode{plural} of {anime}:\n', True)
download(info)


#  End program
kill(f"Process Finished: Downloaded {amount} episodes")
