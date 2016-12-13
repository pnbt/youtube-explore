# Exploring 

This algorithm follows the recommendations on YouTube to find out where they bring you. It saves all videos in a json file, and prints the most recommended videos

## Example of usage:

python follow-youtube-recommendations.py  --query="Do vaccines cause autism?" --searches=4 --branch=4 --depth=4 --name="autism"

* query: query that is made on youtube
* searches: number of search results from the query to start with
* branch: branching factor = number of recommendations that are followed
* name: name under which it will be saved
* alltime: add this option if you want to start from the most viewed videos for the query (using the option filter by viewcount on youtube)

## Results:

All videos, their title, view count, likes, and dislikes are saved in a .json file.

Example results for "Do vaccines cause autism?" ran on 12/12/16:

Most recommended videos:

1) Recommended 20 times:  https://www.youtube.com/watch?v=K1m3TjokVU4 Title: Silent Epidemic; The Untold Story of Vaccines   Movie dire
2) Recommended 16 times:  https://www.youtube.com/watch?v=ze_Hlkz8dDs Title: Madison: Before & After Vaccine Induced Autism
3) Recommended 14 times:  https://www.youtube.com/watch?v=o_nWp6ZHA2Q Title: The Greater Good - Think You Know Everything About Vaccines... Think again.
4) Recommended 13 times:  https://www.youtube.com/watch?v=5ABgp2QomQA Title: 5 Baffling Mysteries About the Universe
5) Recommended 13 times:  https://www.youtube.com/watch?v=o3P6wVUH0pc Title: This is the Best Explanation of the Vaccine/Autism Connection I've Ever Heard!
6) Recommended 11 times:  https://www.youtube.com/watch?v=PQsVTlMsQrI Title: Vacciness -The truth behind vaccinations-
7) Recommended 10 times:  https://www.youtube.com/watch?v=k8-TT87WLBg Title: This Doctor Hates Statin Drugs, Wait Until You Hear Why!
8) Recommended 10 times:  https://www.youtube.com/watch?v=Rzxr9FeZf1g Title: The Science of Anti-Vaccination
9) Recommended 8 times:  https://www.youtube.com/watch?v=BHyV7D-jXKA Title: Sarah Silverman defends abortions and ageism to Bill Maher
10) Recommended 8 times:  https://www.youtube.com/watch?v=kJQjpG-lGY4 Title: Bill Maher vs. an intelligent Christian (Maher loses). *mirror*
...
