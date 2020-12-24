from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

from bs4 import BeautifulSoup, Tag
from requests import get, post

from subprocess import Popen

from os import makedirs
from os.path import exists

from getpass import getuser

from time import sleep



#  Main Host  |  https://www12.9anime.to
#  Data Host  |  https://vidstream.pro



def clear():  #  Clears the terminal
    Popen("cls", shell=True).wait()


# For formatting purposes
clear()


def headless(options):  #  Set Options (selenium) to headless mode
    options.add_argument("--headless")
    return options

def driver():  #  Initiate selenium.webdriver
    return Firefox(options=headless(Options()))



def check(path):  #  Checks if there is an existing directory of the requested anime

    if not exists(path):
        makedirs(path)

    return path + "Episode %s.mp4"



def status(content, new=False, bag=['']):  #  Print over initial print

    if new:
        print(" " * len(bag[-1]), end="\r")
        print(content)
    else:
        content += "..."
        bag.append(content)
        print(content + " " * len(bag[-2]), end="\r")

def inputfmt(content):  #  Formatted for user-input
    return input("%s\n\n\t> " % content)



def getsoup(html):  #  html  ->  BeautifulSoup
    return BeautifulSoup(html, "lxml")

def gethtml(url):  #  requests.get  ->  BeautifulSoup
    return getsoup(get(url).text)

def getjs(driver, urls):  #  webdriver.get  -> BeautifulSoup

    for url in urls:
        driver.get(url)
        sleep(1)
        yield getsoup(driver.page_source)

    driver.quit()



def userlist(titlelist):  #  Formats results [0-9] for selection
    return (lambda MAX: "{1}\n{0}\n{1}".format(f"\n".join("%s [%s]" % (title + " " *(MAX - len(title)), str(index)) for index, title in enumerate(titlelist)), "-" * (MAX + 4))) (len(max(titlelist, key=len)) + 5)

def listsearch(soup):  # FIX LATER // ["data-jtitle"] -> Repetition
    return (lambda DATA: {str(index):[a["data-jtitle"], a["href"]] for index, a in enumerate(DATA)}.get(inputfmt(userlist([a["data-jtitle"] for a in DATA])))) ([li.find("a", class_="name") for li in soup.find("ul", class_="anime-list").find_all("li")[:10]]) if soup.find("ul", class_="anime-list").find("li") else quit(print("Anime not found"))



def sortinput(inp, EPS):  #  Selects applicable episode(s) for download

    try:

        if "-" not in inp:
            if not exists(PATH % inp):
                return [EPS[EPS.index(inp)]]
            else:
                quit(print("Episode already downloaded"))

        else:
            return [ep for ep in EPS[(lambda start, end: slice(start, end + 1)) (*(EPS.index(indice) for indice in inp.split("-")))] if not exists(PATH % ep)]

    except IndexError:
        quit(print("Invalid Episode"))



def grabeps(driver):  #  Grab each episode number from each ul available
    for ul in list(getjs(driver, [EP_FMT.rsplit("/", 1)[0]]))[0].find_all("ul", class_="episodes"):
        for li in ul:
            for a in li:
                if isinstance(a, Tag):  #  Might need Try/Except (ValueError)
                    yield a["data-base"]

def grabkey(soup):  #  Grabs key for specified episode
    return soup.find("div", id="player").find("iframe")["src"].split("?")[0].rsplit("/", 1)[1]

def grabdl(URL):  #  Post request in order to grab downlink link from direct host
    return post(URL, data={"token": gethtml(URL).find("input", type="hidden")["value"]}, headers={"Content-Type": "application/x-www-form-urlencoded"}, stream=True).url



def grabbing(driver, EPISODES):  #  Grabs path and direct download link for each episode
    for path, dl in zip([PATH % ep for ep in EPISODES], [grabdl(VIDSTREAM + grabkey(soup)) for soup in getjs(driver, [EP_FMT % ep for ep in EPISODES])]):
        yield path[:-4].rsplit('\\', 1)[1], path, dl



def download(INFO):  #  Writes the content of each direct download link to the specified path.
    for ep, path, url in INFO:
        with open(path, "wb") as f:
            status("Downloading " + ep)

            for chunk in get(url, stream=True).iter_content(1024):
                f.write(chunk)

            status("Downloaded: " + ep, new=True)




HOST = "https://www12.9anime.to/"
VIDSTREAM = "https://vidstream.pro/download/"


DOWNLOAD_PATH = "C:\\Users\\" + getuser() + "\\Videos\\Anime"



# Grabs title and url of episode if requested anime exists
status("Locating")
ANIME, HREF = listsearch(gethtml(HOST + "search?keyword=" + input(f'Download Path:  "{DOWNLOAD_PATH}"\n\n\t> ').replace(" ", "+")))


# For formatting purposes
clear()


#  Format episode url according to href of anime
status("Found")
EP_FMT = HOST + HREF[1:] + "/ep-%s"


#  Creates new tree if directory of anime title does not exist
PATH = check(DOWNLOAD_PATH + "\\" + (lambda DICT: "".join(DICT.get(char) if char in DICT.keys() else char for char in ANIME)) ({"\\":"-", "/":"-", ":":" -", "*":"", "?":"" , '"':"'", "<":"-", ">":"-", "|": "-"}) + "\\")


#  Grabs each valid episode
status("Grabbing episodes")
EPS = list(grabeps(driver()))


#  Grabs episodes from EPS list according to user input
REQUESTED = sortinput(inputfmt(f"Which Episodes ({EPS[0]}-{EPS[-1]}):"), EPS)


# For formatting purposes
clear()


#  For formatting purposes
PLURAL = "s" if len(REQUESTED) > 1 else ''


#  Grabs direct download from host if applicable episode
status(f"Requesting direct link{PLURAL} from host")
INFO = list(grabbing(driver(), REQUESTED))


# For formatting purposes
clear()


# For formatting purposes
TOPIC, DASH = (lambda STRING: (STRING, "\n%s\n" % ("-" * len(STRING)))) (f"Requested {len(REQUESTED)} episode{PLURAL} of {ANIME}")


#  Downloads each episode to according path
print(f"{TOPIC}{DASH}")
download(INFO)



input(f"{DASH}Press ENTER to exit")
