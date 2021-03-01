#####     Imports     ##############################################################################


from json import dump, load
from os import makedirs
from os.path import exists
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


#  Initiate command within child from newly created process
def call(cmd):
    return Popen(cmd, shell=True).wait()


#  For formatting purposes
def clear():
    call(CLEAR)


#  In case of uncaught exception
def end(reason, kill=True):
    ask(f"Press Enter to exit  |  [{reason}]", True)

    if kill:
        exit()


#  Formatted for user-input
def ask(content, before=False):

    if before:
        clear()

    output = input(content + "\n\n\t> ")
    clear()

    if output == "/exit":
        exit(clear())

    return output


#  Make directory if "path" doesn't exist
def mkdir_if_not_exists(path):
    if not exists(path):
        makedirs(path)


#  Read data file for saved configurations
def r_config():
    with open(config_path, "r") as f:
        return load(f)

#  Dump data to the configuration file
def w_config(data):
    with open(config_path, "w") as f:
        dump(data, f)


#  Format a list in an enumerated fashion
def fmt(l):    
    return (lambda maxl: "\n".join([f"{v}:{' ' * (maxl - len(v))}[{i}]" for i, v in enumerate(l)])) (len(max(l)) + 5)


#  Check if each item from list is within another
def from_in(bag, target):

    for v in bag:
        if v not in target:
            return False
    return True


#  Check if path in 'config.txt' exists
def check_path(path):
    if exists(path):
        return True


#  Remove all duplicates from list
def rm_dupes(mylist):
    for x in mylist:
        while mylist.count(x) > 1:
            mylist.remove(x)

    return mylist


#  Overwrites new path to config.txt
def set_path():
    new_path = ask("Please indicate download path:", True)

    if exists(new_path):
        data = r_config()

        data["path"] = new_path if not new_path.endswith("/") else new_path[:-1]
        w_config(data)
    else:
        set_path()

    return new_path


#  Set langauage filter
def set_language():
    
    try:
        new_language = int(ask("Please indicate language:\n\n" + fmt(LANGUAGES), True))
    except ValueError:
        set_language()

    if new_language in ENUM_LANGUAGES:
        data = r_config()

        data["keys"]["language"] = REAL_LANGUAGES[new_language]
        w_config(data)

    else:
        set_language()


#  Set type(s) filter
def set_type():

    try:
        new_types = rm_dupes(list(map(int, ask("Please indicate type(s):\n\n" + fmt(TYPES), True).split())))
    except ValueError:
        set_type()

    if from_in(new_types, ENUM_TYPES):
        data = r_config()

        data["keys"]["type"] = [REAL_TYPES[x] for x in new_types]
        w_config(data)

    else:
        set_type()

#  Set country filter
def set_country():

    try:
        new_country = int(ask("Please indicate country:\n\n" + fmt(COUNTRIES), True))
    except ValueError:
        set_country()

    if new_country in ENUM_COUNTRIES:
        data = r_config()

        data["keys"]["country"] = REAL_COUNTRIES[new_country]
        w_config(data)
    
    else:
        set_country()


#  Configure downloader  |  Will optimize eventually
def configure(command):

    if command in ("help", "0"):
        configure(ask(f"Search Filter: {get_filter()}\n\n" + fmt(COMMANDS), True))

    elif command in ("path", "1"):
        set_path()

    elif command in ("language", "2"):
        set_language()

    elif command in ("type", "3"):
        set_type()

    elif command in ("country", "4"):
        set_country()

    elif command in ("exit", "5"):
        exit()


#  Get current dl_path
def get_path():
    return r_config()["path"]

#  Get country value for filter
def get_country():
    return r_config()["keys"]["country"]

#  Get language value for filter
def get_language():
    return r_config()["keys"]["language"]

#  Get type value for filter
def get_type():
    return r_config()["keys"]["type"]


#  Get current json configs for filter
def get_filter():

    if not all(r_config().values()):
        return "search?keyword="

    filt = "filter?"

    country = get_country()
    language = get_language()
    type = get_type()

    if country:
        filt += "country[]=" + country + "&"
    
    if language:
        filt += "language[]=" + language + "&"

    if type:
        for t in type:
            filt += "type[]=" + t + "&"

    return filt + "keyword="


#  Set Options (selenium) to headless mode
def get_headless(options: Options):

    options.add_argument("--headless")
    return options


#  Initiate selenium.webdriver
def driver():
    return Firefox(

        options=headless,
        executable_path=geckodriver_path,
        service_log_path=service_log_path

        )


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
def get_html(url):
    return soupify(get_loop(url).text)

#  Firefox().get  ->  BeautifulSoup
def get_js(Driver: Firefox, urls: list, find: expected_conditions):
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


#  Automatically setup geckodriver
def geckodriver(url):
    print("Setting up Geckodriver...")

    res = get(url)

    if res.status_code != 200:
        end("Error with geckodriver")

    file = parent + url.rsplit('/', 1)[1]

    with open(file, "wb") as f:
        for chunk in res.iter_content(1024):
            f.write(chunk)

    command = f"tar -xf {file} -C {parent} && rm {file}"

    if (url[-2:] == "xz"):
        command += f" && mv {parent}usr/bin/geckodriver {parent}geckodriver && rm -r {parent}usr"

    call(command + " && sudo chmod +x geckodriver")


#  Get current python compiler for background process
def get_compiler():
    from ctypes import POINTER, byref, c_char_p, c_int, c_wchar_p, pythonapi
    from sys import version_info

    def update(argv_):
        pythonapi.Py_GetArgcArgv(byref(c_int()), byref(argv_))
        return argv_

    return update(POINTER(c_wchar_p if version_info >= (3, ) else c_char_p) ())[0]


#####     Variables     ############################################################################


#  Sources (Host & Download Server)
MAIN = "https://www13.9anime.to/"
VIDSTREAM = "https://vidstream.pro/download/"

#  Preload prompt
PROMPT = 'Download Path:  "%s"  |  "/help" for commands.'

# Preload 'clear' command
CLEAR = "clear"


#  List of config commands
COMMANDS = ["help", "path", "language", "type", "country", "exit"]


# Languages info
LANGUAGES = ["Dub", "Sub"]
REAL_LANGUAGES = ["dub", "sub"]
ENUM_LANGUAGES = range(len(LANGUAGES))

#  Types info
TYPES = ["Movie", "TV Series", "OVA", "ONA", "Special"]
REAL_TYPES = ["movie", "tv", "ova", "ona", "special"]
ENUM_TYPES = range(len(TYPES))

#  Countries info
COUNTRIES = ["Japan", "China"]
REAL_COUNTRIES = ["120822", "120823"    ]
ENUM_COUNTRIES = range(len(COUNTRIES))


#  Preload headless options
headless = get_headless(Options())

#  Parent path to __file__
parent = __file__.rsplit("/", 1)[0] + "/"

#  Preloaded paths
config_path = parent + "config.json"
geckodriver_path = parent + "geckodriver"
service_log_path = parent + "logging.txt"


#####     Setup     ################################################################################


#  Install `geckodriver` to parent if "geckodriver" not found
if not exists(geckodriver_path):

        github = "https://github.com/mozilla/geckodriver/releases/download/v0.{0}.0/geckodriver-v0.{0}.0-{1}.tar.gz"
        pkgs = "https://eu.mirror.archlinuxarm.org/aarch64/community/geckodriver-0.26.0-1-aarch64.pkg.tar.xz"

        def get_url(m, a):

            if (m == "AMD64"):
                return github.format("29", "linux" + a)

            elif (m == "arm"):
                return github.format("23", "arm7hf")

            elif (m == "aarch64"):
                return pkgs

            else:
                end("Incompatible OS")

        geckodriver(get_url(machine(), architecture()[0][0:2]))



#  Create 'config.json' file if not found within parent
if not exists(config_path):
    w_config({"path": None, "keys": {v: None for v in ("language", "type", "country")}})
