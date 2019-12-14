# Exploring YouTube recommendations

Where does YouTube's recommendation algorithm bring the user if he follows the recommendations?
This robot follows the recommendations on YouTube from a given search query to find out where they bring you.
After searching on YouTube and following the recommendations, it prints the 50 most recommended videos.

## Installation

To install the project's python dependencies, you can use pip:

```
pip install -r requirements
```

Used dependencies:

* [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

## Example of usage:

```shell
follow-youtube-recommendations "global warming,vaccines,nasa" "science" --searches=4 --branch=4 --depth=4
```

* query "global warming,vaccines,nasa": query that is made on youtube
* name "science": name under which it will be saved
* --searches: number of search results from the query to start with
* --branch: branching factor = number of recommendations that are followed
* --alltime: add this option if you want to start from the most viewed videos for the query (using the option filter by viewcount on youtube)
