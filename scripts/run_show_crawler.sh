#!/usr/bin/env bash
source `which virtualenvwrapper.sh`
workon showcrawler
python show_crawler/show_crawler_main.py $1
deactivate