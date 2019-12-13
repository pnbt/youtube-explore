from __future__ import division
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import chr
from builtins import str
from builtins import object
from past.utils import old_div
__author__ = 'Guillaume Chaslot'

"""
    This scripts starts from a search query on youtube and:
        1) gets the N first search results
        2) follows the first M recommendations
        3) repeats step (2) P times
        4) stores the results in a json file
"""

import urllib.request, urllib.error, urllib.parse
import re
import json
import sys
import argparse
import time

from bs4 import BeautifulSoup

RECOMMENDATIONS_PER_VIDEO = 1
RESULTS_PER_SEARCH = 1

# NUMBER OF MIN LIKES ON A VIDEO TO COMPUTE A LIKE RATIO
MIN_LIKES_FOR_LIKE_RATIO = 5

class YoutubeFollower(object):
    def __init__(self, verbose=False, name='', alltime=True, gl=None, language=None, recent=False, loopok=True):
        # Name
        self._name = name
        self._alltime = alltime
        self._verbose = verbose

        # Dict video_id to {'likes': ,
        #                   'dislikes': ,
        #                   'views': ,
        #                   'recommendations': []}
        self._video_infos = {} # self.try_to_load_video_infos()

        # Dict search terms to [video_ids]
        self._search_infos = {}
        self._gl = gl
        self._language = language
        self._recent=recent
        self._loopok=loopok

        print ('Location = ' + repr(self._gl) + ' Language = ' + repr(self._language))

    def clean_count(self, text_count):
        # Ignore non ascii
        ascii_count = text_count.encode('ascii', 'ignore')
        # Ignore non numbers
        p = re.compile(r'[\d,]+')
        return int(p.findall(ascii_count)[0].replace(',', ''))

    def get_search_results(self, search_terms, max_results, top_rated=False):
        assert max_results <= 20, 'max_results was not implemented to be > 20'

        if self._verbose:
            print ('Searching for {}'.format(search_terms))
            if self._alltime:
                print("Sorting search results by number of views")
            else:
                print("Sorting search restuls by relevance")

        # Trying to get results from cache
        if search_terms in self._search_infos and len(self._search_infos[search_terms]) >= max_results:
            return self._search_infos[search_terms][0:max_results]

        # Escaping search terms for youtube
        escaped_search_terms = urllib.parse.quote(search_terms.encode('utf-8'))

        # We only want search results that are videos, filtered by viewcoung.
        #  This is achieved by using the youtube URI parameter: sp=CAMSAhAB
        if self._alltime:
            filter = "CAMSAhAB"
        else:
            if top_rated:
                filter = "CAE%253D"
            else:
                filter = "EgIQAQ%253D%253D"

        url = "https://www.youtube.com/results?sp=" + filter + "&q=" + escaped_search_terms
        if self._gl:
            url = url + '&gl=' + self._gl

        print ('Searching URL: ' + url)

        headers = {}
        if self._language:
            headers["Accept-Language"] = self._language
        url_request = urllib.request.Request(url, headers=headers)
        html = urllib.request.urlopen(url_request)
        soup = BeautifulSoup(html, "lxml")

        videos = []
        for item_section in soup.findAll('div', {'class': 'yt-lockup-dismissable'}):
            video = item_section.contents[0].contents[0]['href'].split('=')[1]
            videos.append(video)

        self._search_infos[search_terms] = videos
        return videos[0:max_results]

    def get_recommendations(self, video_id, nb_recos_wanted, depth, key):
        if video_id in self._video_infos:
            # Updating the depth if this video was seen.
            self._video_infos[video_id]['depth'] = min(self._video_infos[video_id]['depth'], depth)
            print ('a video was seen at a lower depth')

            video = self._video_infos[video_id]
            recos_returned = []
            for reco in video['recommendations']:
                # This line avoids to loop around the same videos:
                if reco not in self._video_infos or self._loopok:
                    recos_returned.append(reco)
                    if len(recos_returned) >= nb_recos_wanted:
                        break
            if self._loopok:
                video['key'].append(key)
            print ('\n Following recommendations ' + repr(recos_returned) + '\n')
            return recos_returned

        url = "https://www.youtube.com/watch?v=" + video_id

        while True:
            try:
                html = urllib.request.urlopen(url)
                break
            except urllib.error.URLError:
                time.sleep(1)
        soup = BeautifulSoup(html, "lxml")

        # Views
        views = -1
        for watch_count in soup.findAll('div', {'class': 'watch-view-count'}):
            try:
                views = self.clean_count(watch_count.contents[0])
            except IndexError:
                pass

        # Likes
        likes = -1
        for like_count in soup.findAll('button', {'class': 'like-button-renderer-like-button'}):
            try:
                likes = self.clean_count(like_count.contents[0].text)
            except IndexError:
                pass

        # Dislikes
        dislikes = -1
        for like_count in soup.findAll('button', {'class': 'like-button-renderer-dislike-button'}):
            try:
                dislikes = self.clean_count(like_count.contents[0].text)
            except IndexError:
                pass

        # Duration
        duration = -1
        for time_count in soup.findAll('meta', {'itemprop': 'duration'}):
            try:
                dur = time_count['content'].replace('PT', '')
                duration = 0
                if 'H' in dur:
                    contents = dur.split('H')
                    duration += int(contents[0]) * 3600
                    dur = contents[1]
                if 'M' in dur:
                    contents = dur.split('M')
                    duration += int(contents[0]) * 60
                    dur = contents[1]
                if 'S' in dur:
                    contents = dur.split('S')
                    duration += int(contents[0])

            except IndexError:
                pass

        pubdate = ""
        for datefield in soup.findAll('meta', {'itemprop': 'datePublished'}):
            try:
                pubdate = datefield['content']
            except IndexError:
                pass

        # Channel
        channel = ''
        for item_section in soup.findAll('a', {'class': 'yt-uix-sessionlink'}):
            if item_section['href'] and '/channel/' in item_section['href'] and item_section.contents[0] != '\n':
                channel = item_section.contents[0]
                channel_id = item_section['href'].split('/channel/')[1]
                break

        if channel == '':
            print ('WARNING: CHANNEL not found')

        # Recommendations
        recos = []
        for video_list in soup.findAll('li', {'class':"video-list-item related-list-item show-video-time"}):
            try:
                recos.append(video_list.contents[1].contents[1]['href'].replace('/watch?v=', ''))
            except IndexError:
                print ('WARNING Could not get a UP NEXT RECOMMENDATION')
                pass

        for video_list in soup.findAll('li', {'class':"video-list-item related-list-item show-video-time related-list-item-compact-video"}):    
            try:
                recos.append(video_list.contents[1].contents[1]['href'].replace('/watch?v=', ''))
            except IndexError:
                print ('WARNING Could not get a RECOMMENDATION')
                pass

        title = ''
        for eow_title in soup.findAll('span', {'id': 'eow-title'}):
            title = eow_title.text.strip()

        if title == '':
            print ('WARNING: title not found')

        if video_id not in self._video_infos:
            self._video_infos[video_id] = {'views': views,
                                           'likes': likes,
                                           'dislikes': dislikes,
                                           'recommendations': recos,
                                           'title': title,
                                           'depth': depth,
                                           'id': video_id,
                                           'channel': channel,
                                           'pubdate': pubdate,
                                           'duration': duration,
                                           'key': []}
            if self._loopok:
                self._video_infos[video_id]['key'].append(key)

        video = self._video_infos[video_id]
        print(video_id + ': ' + video['title'] + ' [' + channel + ']{' + repr(key) +'} ' + str(video['views']) + ' views , recommendations:' + repr(len(recos)))
        return recos[:nb_recos_wanted]

    def get_n_recommendations(self, seed, branching, depth, key):
        if depth is 0:
            return [seed]
        current_video = seed
        all_recos = [seed]
        index = 0
        for video in self.get_recommendations(current_video, branching, depth, key):
            code = chr(index + 97)
            all_recos.extend(self.get_n_recommendations(video, branching, depth - 1, key + code))
            index = index + 1
        return all_recos

    def compute_all_recommendations_from_search(self, search_terms, search_results, branching, depth):
        search_results = self.get_search_results(search_terms, search_results)
        print ('Search results ' + repr(search_results))

        all_recos = []
        ind = 0
        for video in search_results:
            ind += 1
            all_recos.extend(self.get_n_recommendations(video, branching, depth, str(ind)))
            print ('\n\n\nNext search: ')
        all_recos.extend(search_results)
        return all_recos

    def count(self, iterator):
        counts = {}
        for video in iterator:
            counts[video] = counts.get(video, 0) + 1
        return counts

    def go_deeper_from(self, search_term, search_results, branching, depth):
        all_recos = self.compute_all_recommendations_from_search(search_term, search_results, branching, depth)
        counts = self.count(all_recos)
        print ('\n\n\nSearch term = ' + search_term + '\n')
        print ('counts: ' + repr(counts))
        sorted_videos = sorted(counts, key=counts.get, reverse=True)
        return sorted_videos, counts

    def save_video_infos(self, keyword):
        print ('Wrote file:')
        date = time.strftime('%Y%m%d')
        with open('data/video-infos-' + keyword + '-' + date + '.json', 'w') as fp:
            json.dump(self._video_infos, fp)

    def try_to_load_video_infos(self):
        try:
            with open('data/video-infos-' + self._name + '.json', 'r') as fp:
                return json.load(fp)
        except Exception as e:
            print ('Failed to load from graph ' + repr(e))
            return {}

    def count_recommendation_links(self):
        counts = {}
        for video_id in self._video_infos:
            for reco in self._video_infos[video_id]['recommendations']:
                counts[reco] = counts.get(reco, 0) + 1
        return counts

    def like_ratio_is_computed(self, video):
        return int(video['likes']) > MIN_LIKES_FOR_LIKE_RATIO

    def print_graph(self, links_per_video, only_mature_videos=True):
        """
            Prints a file with a graph containing all videos.
        """
        input_links_counts = self.count_recommendation_links()
        graph = {}
        nodes = []
        links = []
        for video_id in self._video_infos:
            video = self._video_infos[video_id]
            if self.like_ratio_is_computed(video):
                popularity = 0
            else:
                popularity = video['likes'] / float(video['likes'] + video['dislikes'])

            nodes.append({'id': video_id, 'size': input_links_counts.get(video_id, 0), 'popularity': popularity, 'type': 'circle', 'likes': video['likes'], 'dislikes': video['dislikes'], 'views': video['views'], 'depth': video['depth']})
            link = 0
            for reco in self._video_infos[video_id]['recommendations']:
                if reco in self._video_infos:
                    links.append({'source': video_id, 'target': reco, 'value': 1})
                    link += 1
                    if link >= links_per_video:
                        break
        graph['nodes'] = nodes
        graph['links'] = links
        with open('./graph-' + self._name + '.json', 'w') as fp:
            json.dump(graph, fp)
        date = time.strftime('%Y-%m-%d')
        with open('./graph-' + self._name + '-' + date + '.json', 'w') as fp:
            json.dump(graph, fp)
        print ('Wrote graph as: ' + './graph-' + self._name + '-' + date + '.json')


    def print_videos(self, videos, counts, max_length):
        idx = 1
        for video in videos[:max_length]:
            try:
                current_title = self._video_infos[video]['title']
                print (str(idx) + ') Recommended ' + str(counts[video]) + ' times: '
                    ' https://www.youtube.com/watch?v=' + video + ' , Title: ' + repr(current_title))
                if idx % 20 == 0:
                    print ('')
                idx += 1
            except KeyError:
                pass

    def get_top_videos(self, videos, counts, max_length_count):
        video_infos = []
        for video in videos:
            try:
                video_infos.append(self._video_infos[video])
                video_infos[-1]['nb_recommendations'] = counts[video]
            except KeyError:
                pass

        # Computing the average recommendations of the video:
        # The average is computing only on the top videos, so it is an underestimation of the actual average.
        if video_infos is []:
            return []
        sum_recos = 0
        for video in video_infos:
            sum_recos += video['nb_recommendations']
        avg = sum_recos / float(len(video_infos))
        for video in video_infos:
            video['mult'] = old_div(video['nb_recommendations'], avg)
        return video_infos[:max_length_count]

def compare_keywords(query, search_results, branching, depth, name, gl, language, recent, loopok, alltime):
    """
        Splits the query into keywords around commas and runs a scrapping from each keyword.
    """

    date = time.strftime('%Y-%m-%d')
    file_name = 'results/' + name + '-' + date + '.json'
    print ('Running, will save the resulting json to:' + file_name)
    top_videos = {}
    for keyword in query.split(','):
        yf = YoutubeFollower(verbose=True, name=keyword, alltime=alltime, gl=gl, language=language, recent=recent, loopok=loopok)
        top_recommended, counts = yf.go_deeper_from(keyword,
                          search_results=search_results,
                          branching=branching,
                          depth=depth)
        top_videos[keyword] = yf.get_top_videos(top_recommended, counts, 1000)
        yf.print_videos(top_recommended, counts, 50)
        yf.save_video_infos(name + '-' + keyword)

    with open(file_name, 'w') as fp:
        json.dump(top_videos, fp)

def main():
    global parser
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--query', help='The start search query')
    parser.add_argument('--name', help='Name given to the file')
    parser.add_argument('--searches', default='5', type=int, help='The number of search results to start the exploration')
    parser.add_argument('--branch', default='3', type=int, help='The branching factor of the exploration')
    parser.add_argument('--depth', default='5', type=int, help='The depth of the exploration')
    parser.add_argument('--alltime', default=False, type=bool, help='If we get search results ordered by highest number of views')
    parser.add_argument('--gl', help='Location passed to YouTube e.g. US, FR, GB, DE...')
    parser.add_argument('--language', help='Languaged passed to HTML header, en, fr, en-US, ...')
    parser.add_argument('--recent', default=False, type=bool, help='Keep only videos that have less than 1000 views')
    parser.add_argument('--loopok', default=False, type=bool, help='Never loops back to the same videos.')
    parser.add_argument('--makehtml', default=False, type=bool,
        help='If true, writes a .html page with the name which compare most recommended videos and top rated ones.')

    args = parser.parse_args()

    if args.loopok:
        print('INFO We will print keys - ' + repr(args.loopok))
    else:
        print('INFO We will NOT be printing keys - ' + repr(args.loopok))

    compare_keywords(args.query, args.searches, args.branch, args.depth, args.name, args.gl, args.language, args.recent, args.loopok, args.alltime)
    return 0

if __name__ == "__main__":
    sys.exit(main())
