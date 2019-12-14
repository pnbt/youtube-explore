#!/usr/bin/env python
# -*- coding: utf-8 -*-
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="youtube-explorer",
    version="0.0.1",
    author="Guillaume Chaslot",
    #  author_email="author@example.com",
    description="Finding YouTube's top recommendations from any query",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pnbt/youtube-explore",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'follow-youtube-recommendations=follow_youtube_recommendations:main'
        ]
    },
    install_require=['beautifulsoup4', 'future'],
)
