#!/usr/bin/env python
# -*- coding: utf-8 -*-
import bs4

import follow_youtube_recommendations as fyr


def test_clean_count():
    text_count = bs4.element.NavigableString('31.418 x ditonton')
    follower = fyr.YoutubeFollower()
    assert follower.clean_count(text_count) == 31418
