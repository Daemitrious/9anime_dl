from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

from bs4 import BeautifulSoup

from requests import get, post

from os import mkdir
from os.path import exists

from time import sleep


options = Options()
options.add_argument("--headless")


H1 = "https://www12.9anime.to"
H2 = "https://vidstream.pro/download/"

HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}


def getsoup(html):  # Alias for BeautifulSoup
    return BeautifulSoup(html, "lxml")


def gethtml(url):  # requests.get -> soup
    return getsoup(get(url).text)


def getjs(url):  # selenium.get -> soup
    driver = Firefox(options=options)
    driver.get(url)
    sleep(1)
    soup = getsoup(driver.page_source)
    driver.close()
    return soup


def grabkey(soup):
    return soup.find("div", id="player").find("iframe")["src"].split("?")[0].rsplit("/", 1)[1]


def grabdl(URL):
    return post(URL, data={"token": gethtml(URL).find("input", type="hidden")["value"]}, headers=HEADERS, stream=True).url


def findserver(url, title):
    SOUP = gethtml(url + title.replace(" ", "+")).find("a", class_="name")

    return SOUP["href"], SOUP["data-jtitle"] if SOUP else None


def usr(content):
    return [x.strip() for x in content.split(",")]


def grabbing(EPISODES):  #  FIX - FIND NEXT EPISODE INSTEAD OF ADDING
    for ep in EPISODES:
        yield PATH % ep.rsplit("-", 1)[1], grabdl(H2 + grabkey(getjs(ep)))  #  ||| AFTER INITIAL FIX ||| FIX - DONT SPLIT | JUST USE ep


def check_path_ep(EPISODES):
    for ep in EPISODES:
        if not exists(PATH % ep):
            yield EP_FMT % ep


def check_path_title(path):
    if not exists(path):
        mkdir(path)
    return path + "Ep %s.mp4"


def download(INFO):
    for path, url in INFO:
        with open(path, "wb") as f:
            for chunk in get(url, stream=True).iter_content(1024):
                f.write(chunk)




ANIME, EPS = usr(input("\n\t> "))


print("Locating...")
OUTPUT = findserver(H1 + "/filter?type[]=tv&language[]=subbed&keyword=", ANIME)


if OUTPUT:
    print("Found...")
    EP_FMT = H1 + OUTPUT[0] + "/ep-%s"
else:
    quit(input("Unavailable Anime"))


if "-" in EPS:
    EPS = range(*[num if index < 1 else num + 1 for index, num in enumerate(map(int, EPS.split("-")))])


PATH = check_path_title(f"C:\\Users\\evand\\Videos\\Anime\\{OUTPUT[1]}\\")


print("Grabbing...")
INFO = list(grabbing(check_path_ep(EPS if isinstance(EPS, range) else [EPS])))


print("Downloading...")
download(INFO)
