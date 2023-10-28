import urllib
import sys
from xml.etree import ElementTree
import spotipy
import spotipy.util as util
import time
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


SPOTIFY_CLIENT_ID = '<FILL_IN>'
SPOTIFY_CLIENT_SECRET = '<FILL_IN>'

LASTFM_API_KEY = 'b25b959554ed76058ac220b7b2e0a026'
SPOTIFY_SCOPE = 'playlist-modify-public'
SPOTIPY_REDIRECT_URI = 'http://example.com/callback/'


@dataclass
class TopPlaylistInfo:
    playlist_name: str
    period: str
    limit: int


TOP_PLAYLIST_INFOS = [
    TopPlaylistInfo("Top 10 | WEEK", '7day', 10),
    TopPlaylistInfo("Top 30 | MONTH", '1month', 30),
    TopPlaylistInfo("Top 50 | YEAR", '12month', 50)
]


class TopPlaylistCreator:

    def __init__(self, spotify_username: str, lastfm_username: str) -> None:
        self.spotify_username = spotify_username
        self.lastfm_username = lastfm_username
        token = util.prompt_for_user_token(
            spotify_username,
            SPOTIFY_SCOPE,
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=SPOTIPY_REDIRECT_URI
        )
        self.sp = spotipy.Spotify(auth=token)
        self.playlists = self.sp.current_user_playlists()

    def get_lastfm_tracks(self, top_playlist_info: TopPlaylistInfo) -> list[dict]:
        """Returns a list of tracks from a Last.fm top-tracks playlist."""
        encoded = urllib.parse.urlencode({
                "method": "user.gettoptracks",
                "user": self.lastfm_username,
                "period": top_playlist_info.period,
                "limit": top_playlist_info.limit,
                "api_key": LASTFM_API_KEY}
        )
        url = f'http://ws.audioscrobbler.com/2.0/?{encoded}'

        response = urllib.request.urlopen(url)
        tree = ElementTree.parse(response)
        root = tree.getroot()
        tracks = []
        for child in root.iter('track'):
            song = self.clean_song_name(child.find('name').text)
            artist = child.find('artist').find('name').text
            tracks.append({
                'song': song,
                'artist': artist
            })
        logger.info("Fetched %s tracks from Last.fm", len(tracks))
        return tracks

    def find_spotify_playlist(self, playlist_name: str) -> dict:
        """Returns a Spotify playlist object if it exists, otherwise None."""
        for playlist in self.playlists['items']:
            if playlist['name'] == playlist_name:
                return playlist
        return None

    def clean_song_name(self, song: str) -> str:
        """Removes unnecessary strings from song names."""
        bad_strings = [' - Remastered', ' - Original', ' - Single Version', ' - Orchestra Version', ' - Long Version']
        for bad_string in bad_strings:
            song = song.replace(bad_string, '')
        return song

    def get_spotify_track_ids(self, lastfm_tracks: list[str]) -> list[str]:
        """Get a list of Spotify track ids from a list of Last.fm tracks."""
        spotify_track_ids = []
        for lastfm_track in lastfm_tracks:
            artist = lastfm_track['artist']
            song_name = self.clean_song_name(lastfm_track['song'])
            query = f"{artist} {song_name}"
            logger.info(query)

            song_dict = self.sp.search(q=query, type='track', limit=1)
            spotify_track_ids.append(song_dict['tracks']['items'][0]['id'])
        logger.info("Fetched %s tracks from Spotify", len(spotify_track_ids))
        return spotify_track_ids

    def create_spotify_playlists(self, top_playlist_info: TopPlaylistInfo) -> None:
        """Creates the Spotify playlist."""

        lastfm_tracks = self.get_lastfm_tracks(top_playlist_info)
        spotify_track_ids = self.get_spotify_track_ids(lastfm_tracks)
        playlist = self.find_spotify_playlist(top_playlist_info.playlist_name)
        if playlist is None:
            logger.info("Playlist creation method was executed")
            playlist = self.sp.user_playlist_create(self.sp.me()['id'], top_playlist_info.playlist_name, public=True, description="Automatically created top-tracks playlist from github.com/NelisG/spotify_top-tracks_playlists")
        self.sp.user_playlist_replace_tracks(self.sp.me()['id'], playlist['id'], spotify_track_ids)


def main() -> None:

    sys_args = sys.argv
    if len(sys_args) != 3:
        raise Exception("A Spotify and Last.fm username should be given as input \n Usage: python main.py <Spotify_username> <Lastfm_username>")
    spotify_username = sys_args[1]
    lastfm_username = sys_args[2]

    top_playlist_creator = TopPlaylistCreator(spotify_username, lastfm_username)
    for top_playlist_info in TOP_PLAYLIST_INFOS:
        top_playlist_creator.create_spotify_playlists(top_playlist_info)


if __name__ == '__main__':
    tic = time.time()
    main()
    toc = time.time()-tic
    logger.info("Program was run in %.2fs", toc)
