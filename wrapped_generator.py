import os
import sys
import requests
import math
from bs4 import BeautifulSoup as bs

import spotipy
from spotipy import util
from spotipy import SpotifyException
from spotipy.oauth2 import SpotifyOAuth

class Wrapped:
    def __init__(self, year, scope='playlist-modify-public'):
        self.spotify_username = os.environ['SPOTIFY_USERNAME']
        self.spotipy_client_id = os.environ['SPOTIPY_CLIENT_ID']
        self.spotipy_client_secret = os.environ['SPOTIPY_CLIENT_SECRET']
        self.lastfm_username = os.environ['LASTFM_USERNAME']
        self.scope = scope
        self.year = year
        self.base_url = f'https://www.last.fm/user/{self.lastfm_username}/library/tracks?from={self.year}-01-01&to={self.year}-12-31&page='
        self.client = None
        self.tracks = []
        self.spotify_tracks = []
        self.playlist = ''

    def login(self):
        token = util.prompt_for_user_token(
            username=self.spotify_username,
            scope=self.scope, 
            client_id=self.spotipy_client_id, 
            client_secret=self.spotipy_client_secret, 
            redirect_uri='http://localhost'
        )
        self.client = spotipy.Spotify(auth=token, auth_manager=SpotifyOAuth(scope=self.scope))

        return self.client

    def populate_list_for_page(self, page):

        title = ''
        artist = ''

        for row in page.find_all('tr'):
            if row.has_attr('class'):
                if row['class'][0] == 'chartlist-row':
                    for element in row.find_all('td'):
                        if element['class'][0] == 'chartlist-name':
                            for anchor in element.find_all('a'):
                                if anchor.has_attr('title'):
                                    title = anchor['title']
                        
                        if element['class'][0] == 'chartlist-artist':
                            for anchor in element.find_all('a'):
                                if anchor.has_attr('title'):
                                    artist = anchor['title']

            if [artist, title] not in self.tracks and artist != '' and title != '':
                self.tracks.append([artist, title])

        return self.tracks

    def request_tracks(self, number=100):
        page_number = math.ceil(number / 50)

        for page in range(1, page_number + 1):
            response = requests.get(self.base_url + str(page))
            soup = bs(response.text, 'html.parser')
            self.tracks = self.populate_list_for_page(soup)

        return self.tracks

    def create_spotify_playlist(self):
        playlist = self.client.user_playlist_create(self.spotify_username, f'Your Top Songs {self.year}', public=True, description='The songs you loved most this year, all wrapped up.')
        self.playlist = str(playlist['uri'])
        return self.playlist

    def search_for_spotify_tracks(self):

        for track in self.tracks:
            res = self.client.search(f'artist:{track[0]} track:{track[1]}', type='track', limit=1)['tracks']['items']
            
            if type(res) == list and len(res) == 1:
                uri = res[0]['uri']
                self.spotify_tracks.append(str(uri))
            
            elif type(res) == dict:
                uri = res['uri']
                self.spotify_tracks.append(str(uri))

            else:
                print(f'Track not found on Spotify: {track[0]}: {track[1]}')

        return self.spotify_tracks

    def populate_spotify_playlist(self):
        try:
            self.client.user_playlist_add_tracks(self.spotify_username, self.playlist, tracks=self.spotify_tracks)
            return True
        except SpotifyException as e:
            print(e)
            return False

if __name__ == '__main__':
    year = sys.argv[1]
    wrapped = Wrapped(year)
    wrapped.login()
    wrapped.request_tracks()
    wrapped.search_for_spotify_tracks()
    wrapped.create_spotify_playlist()
    wrapped.populate_spotify_playlist()