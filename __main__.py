from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

from requests import get, post
from bs4 import BeautifulSoup

from os import makedirs
from os.path import exists

from getpass import getuser

from time import sleep


def headless(options):  #  Set selenium options to headless mode
    options.add_argument("--headless")
    return options

def status(content, bag=['']):  #  Print over initial print
    bag.append(content)
    print(str(content) + " " * len(bag[-2]), end="\r")


#  Hosts
HOST = "https://www12.9anime.to"
VIDSTREAM = "https://vidstream.pro/download/"


#  Headers required for post request
HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}


def usr(content):  #  Manipulates user's input in order to grab anime and episodes(s)
    return [x.strip() for x in content.split(",")]


def getsoup(html):  #  html  ->  BeautifulSoup
    return BeautifulSoup(html, "lxml")

def gethtml(url):  #  requests.get  ->  BeautifulSoup
    return getsoup(get(url).text)

def getjs(driver, urls):  #  webdriver.get  -> BeautifulSoup

    for url in urls:
        status(f"Scraping episode {url.rsplit('-', 1)[1]}...")
        driver.get(url)
        sleep(1)
        yield getsoup(driver.page_source)

    driver.quit()



def grabkey(soup):  #  Grabs key for specified episode
    return soup.find("div", id="player").find("iframe")["src"].split("?")[0].rsplit("/", 1)[1]


def grabdl(URL):  #  Post request in order to grab downlink link from direct host
    return post(URL, data={"token": gethtml(URL).find("input", type="hidden")["value"]}, headers=HEADERS, stream=True).url


def findserver(url, title):  #  Finds title and server of anime

    SOUP = gethtml(url + title.replace(" ", "+")).find("a", class_="name")
    return SOUP["href"], SOUP["data-jtitle"] if SOUP else None


def grabbing(EPISODES):  #  Grabs path and direct download link for each episode

    for path, dl in zip([PATH % ep.rsplit("-", 1)[1] for ep in EPISODES], [grabdl(VIDSTREAM + grabkey(soup)) for soup in getjs(Firefox(options=headless(Options())), EPISODES)]):
        yield path, dl



def check_path_ep(EPISODES):  #  Checks if any of the episodes requested are already downloaded

    for ep in EPISODES:
        if not exists(PATH % ep):
            yield EP_FMT % ep


def check_path_title(path):  #  Checks if there is an existing directory of the requested anime

    if not exists(path):
        makedirs(path)

    return path + "Ep %s.mp4"



def download(INFO):  #  Writes the content of each direct download link to the specified path.

    for path, url in INFO:

        with open(path, "wb") as f:
            status("Downloading " + path[:-4].rsplit('\\', 1)[1])

            for chunk in get(url, stream=True).iter_content(1024):
                f.write(chunk)




#  Path to where the anime is stored
DOWNLOAD_PATH = "C:\\Users\\" + getuser() + "\\Videos\\Anime"



ANIME, EPS = usr(input(f"{DOWNLOAD_PATH}\n\n\t> "))


# Grabs title and url of episode if requested anime exists
status("Locating...")
OUTPUT = findserver(HOST + "/filter?type[]=tv&language[]=subbed&keyword=", ANIME)



if OUTPUT:  #  Checks if inputted anime exists within host
    status("Found...")
    EP_FMT = HOST + OUTPUT[0] + "/ep-%s"
else:
    quit(input("Unavailable Anime"))



if "-" in EPS:  #  Allows for multiple downloads
    EPS = range(*[num if index < 1 else num + 1 for index, num in enumerate(map(int, EPS.split("-")))])



#  Will implement drive changing feature
PATH = check_path_title(DOWNLOAD_PATH + "\\" + OUTPUT[1] + "\\")



#  Grabs direct download from host if applicable episode
status("Grabbing...")
INFO = list(grabbing(list(check_path_ep(EPS if isinstance(EPS, range) else [EPS]))))



#  Downloads each episode to according path
status("Downloading...")  
download(INFO)




input("Press ENTER to exit...")
