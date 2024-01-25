from PyQt6.QtWidgets import (QMainWindow, QApplication, QPushButton, QFileDialog,
                             QListWidget, QListWidgetItem, QComboBox, QLabel,
                             QProgressBar, QSlider, QLineEdit)
from PyQt6 import uic
from PyQt6.QtCore import QSize, QTimer
from PyQt6.QtGui import QIcon, QPixmap

import sys
import re
import time
from os import getlogin, mkdir, path
import shutil

from ymusic import YM
from player import Player

class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()

        # Load the ui file
        uic.loadUi("design/design.ui", self)

        # Create directory for images and playlists
        if path.exists('./.images') == False:
            mkdir('./.images')
        if path.exists('./.playlists') == False:
            mkdir('./.playlists')
        
        # Directory for saved music
        self.folder_name = "C:/Users/" + getlogin() + "/Desktop"
        # Name of clicked button
        self.button_clicked = ''
        self.selected = -1
        self.playlist = 'normal'

        # Yandex Music API and Player
        self.ym = YM()
        self.player = Player()

        #Define list's/download's widgets
        self.directory = self.findChild(QPushButton, "directory")
        self.download = self.findChild(QPushButton, "download")
        self.all = self.findChild(QPushButton, "all")
        self.playlist_songs = self.findChild(QListWidget, "playlist_songs")
        self.playlist_name = self.findChild(QComboBox, "playlist_name")
        self.amount = self.findChild(QLabel, "amount")
        self.update_playlist = self.findChild(QPushButton, "update")

        # Define player's widgets
        self.back = self.findChild(QPushButton, "back")
        self.play = self.findChild(QPushButton, "play")
        self.next = self.findChild(QPushButton, "next")
        self.musicBar = self.findChild(QProgressBar, "musicBar")
        self.musicSlider = self.findChild(QSlider, "musicSlider")
        self.volumeBar = self.findChild(QProgressBar, "volumeBar")
        self.volumeSlider = self.findChild(QSlider, "volumeSlider")
        self.search = self.findChild(QLineEdit, "search")
        self.search_result_list = self.findChild(QListWidget, "search_result_list")
        self.active_song_image = self.findChild(QLabel, "image")
        self.active_song_name = self.findChild(QLabel, "active_song_name")
        self.track_len = self.findChild(QLabel, "track_len")
        self.total_len = self.findChild(QLabel, "total_len")
        self.timer = QTimer(self)

        # Add all User's Playlists
        self.playlist_name.addItems(self.ym.return_playlists())
        self.tracks_changed()

        # Set Volume value
        with open('design/volume.dat') as f:
            self.volume(int(f.readline()))
        self.volumeSlider.sliderReleased.connect(lambda: self.new_volume())
        self.volumeSlider.valueChanged.connect(lambda: self.player.volume(self.volumeSlider.value()))
        
        # Change List of Tracks
        self.playlist_name.currentIndexChanged.connect(self.tracks_changed)

        # Change background color of button back to standart
        self.playlist_name.currentIndexChanged.connect(lambda: self.change_button_color(self.button_clicked))
        self.playlist_songs.currentRowChanged.connect(lambda: self.change_button_color(self.button_clicked))

        # Function of clicked Button
        self.directory.clicked.connect(self.open_directory)
        self.download.clicked.connect(self.download_track)
        self.all.clicked.connect(self.download_all)
        self.playlist_songs.setIconSize(QSize(48, 48))
        self.search_result_list.setIconSize(QSize(48, 48))
        self.update_playlist.clicked.connect(self.update_tracks_list)

        self.play.clicked.connect(self.play_song)
        self.back.clicked.connect(self.back_music)
        self.next.clicked.connect(self.next_music)

        self.playlist_songs.itemDoubleClicked.connect(self.start_music)

        self.timer.setInterval(500)
        self.timer.timeout.connect(self.current_duration)   

        self.musicSlider.sliderReleased.connect(lambda: self.set_time())

        self.playlist_songs.currentRowChanged.connect(self.set_selected)

        self.search.returnPressed.connect(lambda: self.search_result(self.search.text()))
        self.search.textChanged.connect(lambda: self.search_clear())
        self.search_result_list.itemDoubleClicked.connect(lambda: self.start_music('search'))
        self.search_result_list.itemClicked.connect(self.search_download)

    def set_selected(self):
        if self.playlist_songs.currentRow() != -1:
            self.selected = self.playlist_songs.currentRow()
            self.playlist = 'normal'

    # Return list of Tracks and their amount
    def tracks_changed(self):
        playlist = self.playlist_name.currentText()
        self.playlist_songs.clear()

        if path.exists(f'.playlists/{playlist}.txt'):
            with open(f'.playlists/{playlist}.txt', 'r', encoding='utf-8') as f:
                amount = f.readline().strip()
                songs = [track.strip().replace('^', '\n') for track in f.readlines()]
        else:
            songs, amount = self.ym.return_tracks(playlist)

        self.amount.setText(amount)
        for j in songs:
            title = re.sub(r'\W', '', "".join(j.split("\n")))
            self.playlist_songs.addItem(QListWidgetItem(QIcon(f".images/{title}.png"), j))

    # Download selected Track in playlist
    def download_track(self):
        if self.playlist == 'search':
            selected = self.search_result_list.currentRow()
            if self.ym.download(self.folder_name, selected, self.playlist):
                # Change background color of Button to show completed
                self.button_clicked = 'download'
                with open('design/button_style_done.css', 'r') as f:
                    self.download.setStyleSheet(''.join(f.readlines()))
            else:
                self.button_clicked = 'download'
                with open('design/button_style_error.css', 'r') as f: 
                    self.download.setStyleSheet(''.join(f.readlines()))
        else:
            self.playlist = self.playlist_name.currentText()
            for i in range(len(self.playlist_songs.selectedIndexes())):
                selected = self.playlist_songs.selectedIndexes()[i].row()
                if self.ym.download(self.folder_name, selected, self.playlist):
                    # Change background color of Button to show completed
                    self.button_clicked = 'download'
                    with open('design/button_style_done.css', 'r') as f:
                        self.download.setStyleSheet(''.join(f.readlines()))
                else:
                    self.button_clicked = 'download'
                    with open('design/button_style_error.css', 'r') as f: 
                        self.download.setStyleSheet(''.join(f.readlines()))

    # Download All Tracks in playlist
    def download_all(self):
        self.button_clicked = 'all'
        for i in range(self.playlist_songs.count()):
            selected = i
            playlist = self.playlist_name.currentText()
            if self.ym.download(self.folder_name, selected, playlist):
                # Change background color of Button to show completed
                with open('design/button_style_done.css', 'r') as f:
                    self.all.setStyleSheet(''.join(f.readlines()))

    def update_tracks_list(self):
        # Update to current list of tracks in active playlist
        playlist = self.playlist_name.currentText()
        songs, amount = self.ym.return_tracks(playlist)
        
        self.playlist_songs.clear()

        self.amount.setText(amount)
        for j in songs:
            title = re.sub(r'\W', '', ''.join(j.split("\n")))
            self.playlist_songs.addItem(QListWidgetItem(QIcon(f'.images/{title}.png'), j))

    # Change active playlist for download track from search list
    def search_download(self):
        self.playlist = 'search'

    # Change background color of Button back
    def change_button_color(self, button):
        with open('design/button_style_standart.css', 'r') as f:
            if button == 'download':
                self.download.setStyleSheet(''.join(f.readlines()))
            elif button == 'all':
                self.all.setStyleSheet(''.join(f.readlines()))

    # Set active song's name, image and track's len 
    def active_song(self, pList='normal'):
        if self.selected != -1:
            if pList == 'search':
                playlist = 'search'
            else:
                playlist = self.playlist_name.currentText()
            try:
                title = self.ym.active_song_name(self.selected)
                img = self.ym.active_song_image(self.selected)
                track_len = self.ym.active_song_len(self.selected)

                self.musicBar.setMaximum(track_len) # Set maximum of
                self.musicSlider.setMaximum(track_len) # active song

                track_len = time.strftime('%M:%S', time.gmtime(track_len//1000))
                
                self.ym.download('.MusicCache', self.selected, playlist)

                self.active_song_name.setText(title)
                pixmap = QPixmap(img)
                self.active_song_image.setPixmap(pixmap)
                self.track_len.setText(track_len)
            except TypeError:
                pixmap = QPixmap('design/no_image.png')
                self.active_song_name.setText('Not Available')
                self.active_song_image.setPixmap(pixmap)
                self.track_len.setText('00:00')

    # Start music with Double click
    def start_music(self, pList='normal'):
        if path.exists('./.MusicCache') == False:
            mkdir('./.MusicCache')

        if pList == 'search':
            self.ym.search(self.search.text())
            self.playlist_songs.setCurrentRow(-1)

            self.selected = 0
            title = self.ym.active_song_name(self.selected)
            play = re.sub(r'\W', ' ', title)
            play = [play]
            self.active_song(pList)
            self.player.add_music(play)
            self.player.play_music()
            icon = QIcon('design/pause.png')
            self.play.setIcon(icon)
            self.playState = True
            self.timer.start()
        else:
            self.search_result_list.setCurrentRow(-1)

            playlist = self.playlist_name.currentText()
            title, amount = self.ym.return_tracks(playlist)

            play = list(map(lambda x: re.sub(r'\W', ' ', x), title))
            self.active_song()
            self.player.add_music(play)
            self.player.play_music(self.selected)
            icon = QIcon('design/pause.png')
            self.play.setIcon(icon)
            self.playState = True
            self.timer.start()

    # Play/pause active song
    def play_song(self):
        self.player.pause_music()
        if self.player.media_player.is_playing() == 1:
            icon = QIcon('design/play.png')
            self.play.setIcon(icon)
            self.timer.stop()
        else:
            icon = QIcon('design/pause.png')
            self.play.setIcon(icon)
            self.timer.start()

    def next_music(self):
        self.selected += 1
        if self.selected > self.playlist_songs.count() - 1:
            self.selected = 0

        if self.player.media_player.is_playing() == 0:
            icon = QIcon('design/pause.png')
            self.play.setIcon(icon)
            self.timer.start()
        self.active_song()
        self.player.next(self.selected)

    def back_music(self):
        if self.player.media_player.get_media_player().get_time() < 3000:
            self.selected -= 1
            if self.selected < 0:
                self.selected = self.playlist_songs.count() - 1

            if self.player.media_player.is_playing() == 0:
                icon = QIcon('design/pause.png')
                self.play.setIcon(icon)
                self.timer.start()
            self.active_song()
            self.player.back(self.selected)
        else:
            self.player.media_player.get_media_player().set_time(0)

    # Change current length
    def current_duration(self):
        total = self.player.media_player.get_media_player().get_time()
        self.total_len.setText(time.strftime('%M:%S', time.gmtime(total//1000)))
        self.musicSlider.setValue(total)
        pass
    def set_time(self):
        value = self.musicSlider.value()
        self.player.media_player.get_media_player().set_time(value)

    # Set volume
    def volume(self, old):
        self.volumeSlider.setValue(old)
        self.volumeBar.setValue(old)
        self.player.media_player.get_media_player().audio_set_volume(old)
    def new_volume(self):
        with open('design/volume.dat', 'w') as f: 
            f.write(str(self.volumeSlider.value()))

    def search_result(self, text):
        result = self.ym.search(text)
        self.search_result_list.setEnabled(True)

        title = re.sub(r'\W', '', "".join(result.split("\n")))
        self.search_result_list.clear()
        self.search_result_list.addItem(QListWidgetItem(QIcon(".images/" + title + ".png"), result))
    def search_clear(self):
        if self.search.text() == '':
            self.search_result_list.clear()
            self.search_result_list.setEnabled(False)

    # Clear current row
    def mouseReleaseEvent(self, event):
        self.playlist_songs.setCurrentRow(-1)
        self.search_result_list.setCurrentRow(-1)
        self.change_button_color(self.button_clicked)

    # Clear cache
    def closeEvent(self, event):
        self.player.stop_music()
        try:
            shutil.rmtree('./.MusicCache')
        except:
            pass
    
    # Open File Dialog
    def open_directory(self):
        folder_name = QFileDialog.getExistingDirectory(self, "Open Directory", "")
        if folder_name != '':
            self.folder_name = folder_name

if __name__ == '__main__':
    app = QApplication(sys.argv)
    UIWindow = UI()
    UIWindow.show()
    app.exec()