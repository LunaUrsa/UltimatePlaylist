import xml.etree.ElementTree as xml
import os
import numpy
import time

# Define root folder to scan
media_path = "E:\TV - Good"
print(f"Scanning folder: {media_path}")

# Determines where the file is being saved, either locally for easy-open or in the media folder
debug_mode = False
print(f"Debug mode: {debug_mode}")

# Saves the file as if you were to play it on your home PC
# Set to false to append network address
save_local = False
print(f"Savig locally: {save_local}")

class Playlist:
    """Build xml playlist."""
    
    def __init__(self):
    #Defines basic tree structure.
        self.playlist = xml.Element('playlist')
        self.tree = xml.ElementTree(self.playlist)
        self.playlist.set('xmlns','http://xspf.org/ns/0/')
        self.playlist.set('xmlns:vlc','http://www.videolan.org/vlc/playlist/ns/0/')
        self.playlist.set('version', '1')

        self.title = xml.Element('title')
        self.playlist.append(self.title)
        self.title.text = 'Playlist'

        self.trackList = xml.Element('trackList')
        self.playlist.append(self.trackList)

    def add_track(self, path):
    #Add tracks to xml tree (within trackList).
        track = xml.Element('track')
        location = xml.Element('location')
        location.text = path
        track.append(location)
        self.trackList.append(track)
    
    def get_playlist(self):
    #Return complete playlist with tracks.
        return self.playlist

class Videos:
    """Manage files (videos) to be added to the playlist."""
    def __init__(self):
        pass

    def get_videos(self, media_path):
    #Returns list of files in the directory.

        # Get a list of all TV shows
        CD = os.getcwd()
        print(f"Current directory: {CD}")
        all_series = os.listdir(CD)
        # print(f"all series: {all_series}")
        show_dict = {}
        for series_name in all_series:
            series_path = media_path + "\\" + series_name
            print(f"Series path: {series_path}")
            if series_name == ".deletedByTMM":
                continue
            if not os.path.isdir(series_path):
                print(f"Not a path: {series_path}")
                continue
            print("    " + series_name)
            show_dict[series_name] = []
            all_seasons = os.listdir(series_path)
            for season_name in all_seasons:
                season_path = os.path.join(series_path, season_name)
                if os.path.isdir(season_path):
                    # print('        ' + season_name)
                    episodes = os.listdir(season_path)
                    for episode_name in episodes:
                        # if any(x in episode_name for x in media_types):
                        episode_path = os.path.join(season_path, episode_name)
                        # print('            ' + episode_name)
                        show_dict[series_name].append(episode_path)
                        #print('                ' + episode_path)

            # break
        return show_dict

    def remove_nonvideo_files(self,video_dict):
    #Removes files whose extension is not mentioned in ext_list from list of files.
        # Define valid media types
        #List of extensions to be checked.
        ext_list = [".M2TS",".3g2",".3gp",".amv",".asf",
        ".flv",".flv",".gif",".gifv",".m2v",".m4p",".m4v",
        ".avi",".drc",".f4a",".f4b",".f4p",".f4v",".webm",
        ".mpeg",".m4v",".mpg",".mpg",".mpv",".MTS",".mxf",
        ".mpeg",".mkv",".mng",".mov",".mp2",".mp4",".mpe",
        ".nsv",".ogg",".ogv",".qt",".rm",".rmvb",".roq",
        ".svi",".TS",".viv",".vob",".wmv",".yuv",".flv"]

        for series_name in video_dict:
            file_list = video_dict[series_name]
            for index,file_name in enumerate(file_list[:]):
                if file_name.endswith(tuple(ext_list)) or file_name.endswith(tuple(ext.upper() for ext in ext_list)):
                    pass
                else:
                    # print("removed " + file_name)
                    file_list.remove(file_name)
            video_dict[series_name] = file_list
        return video_dict
    
    def equalize(self, video_dict):
    #Make each show appear an equal amount of times
        simpsons_episodes = len(video_dict["The Simpsons (1987)"])
        if debug_mode:
            print(f"There are {simpsons_episodes} episodes of The Simpsons")
            
        for series_name in video_dict:
            total_episodes = len(video_dict[series_name])
            if not total_episodes:
                continue
            simpsons_units = round(simpsons_episodes/total_episodes,0)

            i = 1
            episode_list = video_dict[series_name]
            new_episode_list = episode_list
            while i < simpsons_units:
                # print(f"{i} times equalizing {series_name}")
                new_episode_list = numpy.append(new_episode_list,episode_list)
                i += 1

            video_dict[series_name] = new_episode_list

            end_episodes = len(video_dict[series_name])
            end_su = round(636/end_episodes,0)
            if debug_mode:
                print(f"{series_name} has {total_episodes} ({simpsons_units}SU) and was expanded to {end_episodes} episodes ({end_su}SU)")

        return video_dict

    def randomize(self, video_dict):
        video_list = []
        for series_name in video_dict:
            episode_list = video_dict[series_name]
            numpy.random.shuffle(episode_list)
            for episode_path in episode_list:
                video_list.append(episode_path)
            # for episode_path in video_dict[series_name]:
            #     video_list.append(episode_path)
        numpy.random.shuffle(video_list)
        return video_list

    def edit_paths(self, video_files):
    #Add path and prefix to files as required in vlc playlist file.
        for index in range(len(video_files)):
            file_path = ('file:///' + os.path.join(video_files[index])).replace('\\','/')
            # print(f"save_local {save_local}")
            file_path = (file_path).replace('E:','\\\\LUNABOX')
            # if debug_mode:
            #     print(f"Modified path to: {file_path}")
            video_files[index] = (file_path)

        return video_files

def main():
    print("9 - Initializing Playlist module")
    playlist = Playlist()
    print("8 - Initializing Videos module")
    videos = Videos()
    print("7 - Getting list of files!!!!")
    files_dict = videos.get_videos(media_path)
    print("6 - Removing nonvideo files")
    video_dict = videos.remove_nonvideo_files(files_dict)
    print("5 - Equalizing episodes per series")
    # video_files = videos.equalize(video_dict)
    print("4 - Randomizing videos")
    random_files = videos.randomize(video_dict)
    print("3 - Editing video paths for VLC playlists")
    video_paths = videos.edit_paths(random_files)
    print("2 - Adding videos to playlist")
    for path in video_paths:
        playlist.add_track(path)
    print("1 - Saving playlist file")
    playlist_xml = playlist.get_playlist()
    save_path = media_path + '\EricTV.xspf'
    if debug_mode:
        save_path = "EricTV.xspf"
    with open(save_path,'w') as mf:
        mf.write(xml.tostring(playlist_xml).decode('utf-8'))
        print(f"0 - File has been saved to {save_path}")
    print("Exiting in 3...", end = "\r")
    time.sleep(1)
    print("Exiting in 2...", end = "\r")
    time.sleep(1)
    print("Exiting in 1...", end = "\r")
    time.sleep(1)
    input()
main()

'''
playlist(ROOT)
    title /title
    trackList
        track
            location file:///path /location
            title                  /title
            image                  /image
            duration              /duration
        /track
    /tracklist
/playlist
'''