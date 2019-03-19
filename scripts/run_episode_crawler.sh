#!/usr/bin/env bash
source `which virtualenvwrapper.sh`
workon episodecrawler
python episode_crawler/episode_crawler_main.py
deactivate