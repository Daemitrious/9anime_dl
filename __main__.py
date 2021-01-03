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



def clear():
    Popen("cls", shell=True).wait()


clear()



def kill(reason): 
    exit(input("\n" + reason))


def status(content, static=False, bag=['']):  #  Print over initial print

    if static:
        print(" " * len(bag[-1]) + "\r" + content)
    else:
        content += "..."
        bag.append(content)
        print(content + " " * len(bag[-2]), end="\r")


def ask(content):  #  Formatted for user-input
    output = input(content + "\n\n\t> ")
    clear()
    return output


def headless(options):  #  Set Options (selenium) to headless mode
    options.add_argument("--headless")
    return options

def driver():  #  Initiate selenium.webdriver
    return Firefox(options=headless(Options()))


def ec(xpath):
    return expected_conditions.visibility_of_element_located((By.XPATH, xpath))


def mkdir_if_exists(path):
    if not exists(path):
        makedirs(path)


def soupify(html):  #  html  ->  BeautifulSoup
    return BeautifulSoup(html, "lxml")


def gethtml(url):  #  requests.get  ->  BeautifulSoup
    return soupify(get(url).text)

def getjs(Driver, urls, find):
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
    return (lambda MAX: 'Search results from "{0}"\n\n{2}\n{1}\n{2}'.format(anime, "\n".join(("%s%s[%i]" % (t, " " * (MAX - len(t)), i) for i, t in enumerate(titlelist))), "-" * (MAX  + 3))) (len(max(titlelist, key=len)) + 5)

def show_dict(data):
    return {str(i): th for i, th in enumerate(data)}


def listsearch(soup):
    if soup.find("ul", class_="anime-list").find("li"):
        return (lambda data: show_dict(data).get(ask(show_list([t[0] for t in data])))) ([(a["data-jtitle"], a["href"][1:]) for a in [li.find("a", class_="name") for li in soup.find("ul", class_="anime-list").find_all("li")[:10]]])
    else:
        kill("Anime not found")


def sortinput(inp, EPS):  #  Selects applicable episode(s) for download

    try:
        if "-" not in inp:
            if not exists(PATH % inp):
                return [EPS[EPS.index(inp)]]
            else:
                kill("Episode already downloaded")

        else:
            return [ep for ep in EPS[(lambda start, end: slice(start, end + 1)) (*(EPS.index(indice) for indice in inp.split("-")))] if not exists(PATH % ep)]

    except IndexError:
        kill("Invalid Episode")


def grabeps(driver):  #  Grab each episode number from each ul available
    for ul in list(getjs(driver, EP_FMT.rsplit("/", 1)[0], ec("//ul[@class='episodes']")))[0].find_all("ul", class_="episodes"):
        for li in ul:
            for a in li:
                if isinstance(a, Tag):  #  Might need Try/Except (ValueError)
                    yield a["data-base"]

def grabkey(soup):  #  Grabs key for specified episode
    return soup.find("div", id="player").find("iframe")["src"].split("?")[0].rsplit("/", 1)[1]

def grabdl(URL):  #  Post request in order to grab downlink link from direct host
    return post(URL, data={"token": gethtml(URL).find("input", type="hidden")["value"]}, headers={"Content-Type": "application/x-www-form-urlencoded"}, stream=True).url


def grabbing(driver, EPISODES):  #  Grabs path and direct download link for each episode
    return [(path[:-4].rsplit("\\", 1)[1], path, dl) for path, dl in zip([PATH % ep for ep in EPISODES], [grabdl(VIDSTREAM + grabkey(soup)) for soup in getjs(driver, [EP_FMT % ep for ep in EPISODES], ec("//div[@id='player']//iframe"))])]


def download(INFO):  #  Writes the content of each direct download link to the specified path.
    for ep, path, url in INFO:
        with open(path, "wb") as f:
            status("Downloading " + ep)

            for chunk in get(url, stream=True).iter_content(1024):
                f.write(chunk)

            status("Downloaded: " + ep, True)



MAIN = "https://www12.9anime.to/"
VIDSTREAM = "https://vidstream.pro/download/"


PATH = "C:\\Users\\" + getuser() + "\\Videos\\Anime"


FILTER = {"\\":"-", "/":"-", ":":" -", "*":"", "?":"" , '"':"'", "<":"-", ">":"-", "|": "-"}


anime = ask(f'Download Path:  "{PATH}"')

# Grabs title and server of anime specified
status("Locating")
ANIME, HREF = listsearch(gethtml(MAIN + "search?keyword=" + anime.replace(" ", "+")))


#  Format episode url according to href of anime
status("Found")
EP_FMT = MAIN + HREF + "/ep-%s"


#  Creates new tree if directory of anime title does not exist
PATH += f"\\{''.join(map(lambda char: FILTER.get(char) if char in FILTER.keys() else char, ANIME))}\\Episode %s.mp4"


#  Grabs each valid episode
status("Grabbing episodes")
EPS = list(grabeps(driver()))


#  Grabs episodes from EPS list according to user input
REQUESTED = sortinput(ask(f"Which Episodes ({EPS[0]}-{EPS[-1]}):"), EPS)


#  For formatting purposes
PLURAL = "s" if len(REQUESTED) > 1 else ''


#  Grabs direct download from host if applicable episode
status(f"Requesting direct link{PLURAL} from host")
INFO = grabbing(driver(), REQUESTED)


mkdir_if_exists(PATH.rsplit("\\", 1)[0])


#  Downloads each episode to according path
status(f"Requested {len(REQUESTED)} episode{PLURAL} of {ANIME}")
download(INFO)


input("Press ENTER to exit")
