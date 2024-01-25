from yandex_music import Client
from os import path
import re

client = Client('Token')
client.init()

class YM:
    def __init__(self):
        self.playlist_list = []
        self.tracks_normal_list = []
        self.users_playlists = client.users_playlists_list()
        self.users_likes = client.users_likes_tracks()
        self.tracks = []
        self.search_tracks = []

    def return_playlists(self):
        # List of User's Playlists
        for i in self.users_playlists:
            self.playlist_list.append(i.title)
        self.playlist_list.append('Мне нравится')
        return self.playlist_list

    def return_tracks(self, playlist):
        # List of Tracks in  Playlist
        if playlist == 'Мне нравится':
            # User's likes tracks
            self.tracks = self.users_likes.fetch_tracks()
            amount_tracks = str(len(self.tracks)) + ' tracks'
        else:
            # User's playlist
            pList = self.playlist_list.index(playlist)
            tracks_list = self.users_playlists[pList]
            self.tracks = tracks_list.tracks if tracks_list.tracks else tracks_list.fetch_tracks()

            amount_tracks = str(self.users_playlists[pList].track_count) + ' tracks'

        # Readable List of Tracks
        self.tracks_normal_list.clear()
        for short_track in self.tracks:

            # Main playlist or User's playlist
            if playlist != 'Мне нравится':
                track = short_track.track if short_track.track else short_track.fetch_track()
            else:
                track = short_track

            # Change Not Available Track
            if track.available == False:
                self.tracks_normal_list.append("Not Available")
                continue

            
            full_artists = []
            for i in range(len(track.artists)):
                full_artists.append(track.artists[i].name)

            self.tracks_normal_list.append(track.title + '\n' + ', '.join(full_artists))

            # Save Track's image
            title = re.sub(r'\W', '', track.title)
            artist = re.sub(r'\W', '', ' '.join(full_artists))
            if path.exists('.images/' + title + artist + '.png') or track.cover_uri is None:
                continue
            else:
                track.download_cover('.images/' + title + artist + '.png', size='400x400')

        with open(f'.playlists/{playlist}.txt', 'w', encoding='utf-8') as f:
            f.write(amount_tracks + '\n')
            f.writelines([track.replace('\n', '^') + '\n' for track in self.tracks_normal_list])

        return self.tracks_normal_list, amount_tracks

    # Download Track
    def download(self, direct, selected, playlist):
        if self.tracks_normal_list[selected] == 'Not Available':
            # Do not download
            return False
        else:
            title = re.sub(r'\W', ' ', self.tracks_normal_list[selected])
            if path.exists(f'{direct}/{title}.mp3'):
                return True
            else:
                if playlist == 'Мне нравится' or playlist == 'search':
                    self.tracks[selected].download(f'{direct}/{title}.mp3')
                else:
                    self.tracks[selected].fetch_track().download(f'{direct}/{title}.mp3')
                return True

    # Return active song's title, image and len         
    def active_song_name(self, selected):
        if self.tracks_normal_list[selected] == 'Not Available':
            return False
        else:
            title = self.tracks_normal_list[selected]
            return title
        
    def active_song_image(self, selected):
        if self.tracks_normal_list[selected] == 'Not Available':
            return False
        else:
            img = re.sub(r'\W', '', self.tracks_normal_list[selected])
            return ".images/" + img + ".png"

    def active_song_len(self, selected):
        if self.tracks_normal_list[selected] == 'Not Available':
            return False
        else:
            try: 
                track_len = self.tracks[selected].fetch_track().duration_ms
            except:
                track_len = self.tracks[selected].duration_ms
            return track_len
        
    def search(self, query):
        search_result = client.search(query)

        best_result_text = ''
        if search_result.best:
            type_ = search_result.best.type
            best = search_result.best.result

            if type_ in ['track', 'podcast_episode']:
                artists = ''
                if best.artists:
                    artists = '\n' + ', '.join(artist.name for artist in best.artists)
                best_result_text = best.title + artists
            elif type_ == 'artist':
                best_result_text = best.name
            elif type_ in ['album', 'podcast']:
                best_result_text = best.title
            elif type_ == 'playlist':
                best_result_text = best.title
            elif type_ == 'video':
                best_result_text = f'{best.title} {best.text}'

        try:
            title = re.sub(r'\W', '', best_result_text)
            best.download_cover('.images/' + title + '.png', size='400x400')
        except:
            pass
        
        self.playlist_list.append('search')
        self.tracks.clear()
        self.tracks.append(best)
        self.tracks_normal_list.clear()
        self.tracks_normal_list.append(best_result_text)
        return best_result_text

