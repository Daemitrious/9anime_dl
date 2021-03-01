from sys import argv

from relative import VIDSTREAM, driver, ec, get, get_html, get_js, post


#  Grabs key for specified episode
def grabkey(soup):
    return soup.find("div", id="player").find("iframe")["src"].split("?")[0].rsplit("/", 1)[1]

#  Post request in order to grab downlink link from direct host
def grabdl(URL):
    return post(URL, data={"token": get_html(URL).find("input", type="hidden")["value"]}, headers={"Content-Type": "application/x-www-form-urlencoded"}, stream=True).url


#  Grabs path and direct download link for each episode
def grabbing(driver, path, epurl, episodes):
    for p, soup in zip([path % ep for ep in episodes], get_js(driver, [epurl % ep for ep in episodes], ec("//div[@id='player']//iframe"))):
        yield p, grabdl(VIDSTREAM + grabkey(soup))


#  Writes the content of each direct download link to the specified path.
def download(info):

    for p, url in info:
        with open(p, "wb") as f:
            for chunk in get(url, stream=True).iter_content(1024):
                f.write(chunk)


#  Begin downloading process
download(grabbing(driver(), argv[1].replace("_", " "), argv[2], argv[3:]))
