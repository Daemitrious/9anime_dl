# 9anime_dl

Anime Downloader scraping from 9anime.

# *Requirements*

- **Selenium** installed using `pip3 install selenium` and should also be added to the **PATH** under *System Variables* of *System Environmental Variables*

# **Planning**
- It works (for the most part) but it is atrociously slow as of now because it downloads from *9anime's* `vidstream` server.
- I am planning on scraping directly from their API which should reduce the amount of times `Selenium` is needed.
