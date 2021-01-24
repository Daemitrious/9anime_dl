#####     Imports     ##############################################################################


from os import getcwd, makedirs
from os.path import dirname, exists
from platform import architecture, machine
from subprocess import Popen

from bs4 import BeautifulSoup, Tag
from requests import ReadTimeout, get, post
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


#####     Functions     ############################################################################


#  For formatting purposes
def clear():
    Popen("clear", shell=True).wait()


#  In case of uncaught exception
def end(reason, kill=True):
    ask(f"Press Enter to exit  |  [{reason}]", True)

    if kill == True:
        exit()


#  Formatted for user-input
def ask(content, before=False):

    if before:
        clear()

    output = input(content + "\n\n\t> ")

    clear()

    return output


#  Make directory if "path" doesn't exist
def mkdir_if_not_exists(path):
    if not exists(path):
        makedirs(path)


#  Overwrites new path to config.txt
def change_path():
    new_path = ask("Please indicate download path:", True)

    if new_path:
        with open(config_path, "w") as f:
            f.write(new_path if not new_path.endswith("/") else new_path[:-1])

#  Configure downloader
def config(command):

    if command == "help":  #  Will fix later, if I feel like it.
        config(ask("- help\n- path\n- exit"))

    elif command == "path":
        change_path()

    elif command == "exit":
        end("Exit request")


#  Read data file for saved configurations
def readconfig():
    with open(config_path, "r") as f:
        return f.read()


#  Set Options (selenium) to headless mode
def headless(options: Options):

    options.add_argument("--headless")
    return options

#  Initiate selenium.webdriver
def driver():
    return Firefox(options=headless(Options()), executable_path=geckodriver_path, service_log_path=parent + "logging.txt")

#  Premade EC for WebDriverWait
def ec(xpath):
    return expected_conditions.visibility_of_element_located((By.XPATH, xpath))


#  Continuously retry to get successful response
def get_loop(url):
    while True:
        try:
            res = get(url, timeout=5)

            if res.status_code == 200:
                return res

        except ReadTimeout:
            continue


#  html  ->  BeautifulSoup
def soupify(html):
    return BeautifulSoup(html, "lxml")

#  url  _>  Response
def gethtml(url):
    return soupify(get_loop(url).text)

#  Firefox.get  ->  BeautifulSoup
def getjs(Driver: Firefox, urls: list, find: expected_conditions):
    """
    Iterates through a list of urls and returns a BeautifulSoup object when the expected_condition is found
    """
    Wait = WebDriverWait(Driver, 10, 3)

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


def geckodriver(url):
    print("Setting up Geckodriver...")
    
    res = get(url)

    if res.status_code != 200:
        end("Error with geckodriver")

    file = parent + url.rsplit('/', 1)[1]

    with open(file, "wb") as f:
        for chunk in res.iter_content(1024):
            f.write(chunk)

    for cmd in (

        f"tar -xvzf {file} -C {parent}",
        f"rm {file}",
        f"chmod +x geckodriver",

    ):  Popen(cmd, shell=True).wait()


#####     Variables     ############################################################################


#  Sources (Host & Download Server)
MAIN = "https://www12.9anime.to/"
VIDSTREAM = "https://vidstream.pro/download/"

#  Preload prompt
PROMPT = 'Download Path:  "%s"  |  "/help" for commands.'


parent = (lambda cwd, dn: dn if cwd == dn[:len(cwd)] else cwd + dn) (getcwd() + "/", dirname(__file__) + "/")

config_path = parent + "config.txt"
geckodriver_path = parent + "geckodriver"


#####     Setup     ################################################################################


if not exists(geckodriver_path):
    geckodriver(
        (lambda v, m: f"https://github.com/mozilla/geckodriver/releases/download/v0.{v}.0/geckodriver-v0.{v}.0-{m}.tar.gz") (
            *(("29", "linux" + architecture()[0][0:2]) if machine()[:3] != "arm" else ("23", "arm7hf"))
        )
    )
