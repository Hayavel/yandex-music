import vlc

class Player:
    def __init__(self):
        
        self.player_ = vlc.Instance()
        self.media_list = self.player_.media_list_new()
        self.media_player = self.player_.media_list_player_new()

    def play_music(self, index=0):
        self.media_player.set_media_list(self.media_list)
        self.media_player.play_item_at_index(index)

    def pause_music(self):
        if self.media_player.is_playing() == 1:
            self.media_player.set_pause(1)
        else:
            self.media_player.set_pause(0)
    
    def volume(self, value):
        self.media_player.get_media_player().audio_set_volume(value)

    def stop_music(self):
        self.media_player.stop()

    def add_music(self, titles):
        self.media_list = self.player_.media_list_new()
        for title in titles:
            
            media = self.player_.media_new('.MusicCache/' + title + '.mp3')
            self.media_list.add_media(media)

    def next(self, index):
        self.media_player.play_item_at_index(index)
    
    def back(self, index):
        self.media_player.play_item_at_index(index)
