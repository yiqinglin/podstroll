# podstroll
The conglomeration of podcast crawlers.

## podcrawler
Crawls podcast index from itunes using Scrapy and saves the results into MongoDB.

To start the crawler, run

```
scrapy crawl podcasts
```

## show_crawler
For each podcast crawled in podcrawler, show_crawler looks up its feed url and gets additional show information from its feed.
To start the crawler, run

```
python show_crawler/show_crawler_main.py feed
```

To update feed url, then run

```
python show_crawler/show_crawler_main.py metadata
```
To update show metadata.

## episode_crawler
Pull episode information from individual podcast's feed url.

To start the crawler, run

```
python episode_crawler/episode_crawler_main.py
```