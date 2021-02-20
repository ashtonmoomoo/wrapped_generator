import os
import requests
from bs4 import BeautifulSoup as bs

import spotipy
from spotipy import util
from spotipy import SpotifyException
from spotipy.oauth2 import SpotifyOAuth

spotify_username = os.environ['SPOTIFY_USERNAME']
spotipy_client_id = os.environ['SPOTIPY_CLIENT_ID']
spotipy_client_secret = os.environ['SPOTIPY_CLIENT_SECRET']
lastfm_username = os.environ['LASTFM_USERNAME']

scope = 'playlist-modify-public'

year = '2016' # Year to generate wrapped playlist for

base_url = f'https://www.last.fm/user/{lastfm_username}/library/tracks?from={year}-01-01&to={year}-12-31&page='

token = util.prompt_for_user_token(
    username=spotify_username,
    scope=scope, 
    client_id=spotipy_client_id, 
    client_secret=spotipy_client_secret, 
    redirect_uri="http://localhost"
)
sp = spotipy.Spotify(auth=token, auth_manager=SpotifyOAuth(scope=scope))

def populate_list_for_page(page, tracks):

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

        if [artist, title] not in tracks and artist != '' and title != '':
            tracks.append([artist, title])

    return tracks

def get_tracks():
    tracks = []
    for page in [1, 2]:
        response = requests.get(base_url + str(page))
        soup = bs(response.text, 'html.parser')
        tracks = populate_list_for_page(soup, tracks)

    return tracks

def create_playlist():
    playlist = sp.user_playlist_create(spotify_username, f'Your Top Songs {year}', public=True, description='The songs you loved most this year, all wrapped up.')
    return str(playlist['uri'])

def search_for_spotify_tracks(tracks):
    spotify_tracks = []

    for track in tracks:
        res = sp.search(f'artist:{track[0]} track:{track[1]}', type='track', limit=1)['tracks']['items']
        
        if type(res) == list and len(res) == 1:
            uri = res[0]['uri']
            spotify_tracks.append(str(uri))
        
        elif type(res) == dict:
            uri = res['uri']
            spotify_tracks.append(str(uri))

        else:
            print('Track not found on Spotify:')
            print(track[0] + ': ' + track[1])

    return spotify_tracks

def populate_playlist(playlist, tracks):
        try:
            sp.user_playlist_add_tracks(spotify_username, playlist, tracks=tracks)
        except SpotifyException as e:
            print(e)

if __name__ == '__main__':
    tracks = get_tracks()
    empty_playlist = create_playlist()
    spotify_tracks = search_for_spotify_tracks(tracks)
    populate_playlist(empty_playlist, spotify_tracks)