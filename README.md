***Idle Anime Downloader*** - Scrapes from *https://www12.9anime.to*

# 9anime_dl
- Supported Platforms: **Linux**

# Description
Because 9anime does NOT like it when people download their content using bots or whatever, they limit the bandwitch usage to about 1MB for downloads.  Other than the downloading process, which is slow as shit, it should take around a solid half a minute to get it going, that being said, typing in the anime that you want, selecting it, then specifying how many episodes you want.  After all of that, you just sit and chillaxe as it downloads in the background, and it will automatically write the videos into a dedicated folder.  Also, because the content isn't being stored into memory before writing, you should be able to watch it as it downloads, as long as you don't skip ahead to far.

# *Requirements*

`pip3 install requests bs4 lxml selenium`

If you do not have a 'geckodriver' in the same directory as `9anime_dl` then it will automatically grab a compatible version from the official Mozilla Geckodriver Github repository.  If you want to use a specific version, then just place it inside of the same directory as `__main__.py` and make sure it has the name "geckodriver".

- *Add [webdriver][1] to **PATH** under *System Variables* of *System Environmental Variables**




[1]: https://github.com/mozilla/geckodriver/releases
