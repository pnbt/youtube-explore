# youtube-explore

This algorithm follows the recommendations on youtube to find out where they bring you!

example usage:

python follow-youtube-recommendations.py  --query="trump" --searches=3 --branch=3 --depth=6 --name="trump-336"

--query: query that is made on youtube
--searches: number of search results from the query to start with
--branch: branching factor = number of recommendations that are followed
--name: name under which it will be saved
--alltime: add this option if you want to start from the most viewed videos for the query (using the option filter by viewcount on youtube)

