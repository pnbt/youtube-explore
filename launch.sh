#!/bin/sh
python follow-youtube-recommendations.py --depth=6 --branch=3 --searches=3 --query="trump" --name="trump-336"
python follow-youtube-recommendations.py --depth=6 --branch=3 --searches=3 --query="clinton" --name="clinton-336"
python follow-youtube-recommendations.py --depth=5 --branch=5 --searches=5 --query="trump" --name="trump-5"
python follow-youtube-recommendations.py --depth=5 --branch=5 --searches=5 --query="clinton" --name="clinton-5"



