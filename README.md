# GearMusic
GearMusic is a simple python library for adding, listing and removing musics on a Samsung Gear S2 or Gear S3 device.

# How To Use?
First, you have to create a Gear object, that represents your Gear device.

    mygear = Gear('192.168.1.218')
    
Since, you have to accept the connexion on your smartwatch.
While accepting, you can use something like that:

    print ('Waiting for accepting connexion...')
    mygear.wait_for_connexion()
    print ('Connexion accepted!')
    
Now, you can manage your tracks. For exemple, you can list all tracks on the gear device with:

    mygear.tracks
    >>> [<Track "Bohemian Rhapsody" by "Queen">, <Track "Uprising" by "Muse">, ...]
    
A Track object represents a track present on a Gear device.
It has multiple attributes, which are:

 - track.title (string) : The title of the song
 - track.artist (string) : The artist of the song
 - track.album (string) : The album of the song
 - track.duration (datetime.timedelta) : The duration of the song
 - track.size (int) : The size of the song (in bytes)
 - track.path (string) : The path of the file on the device
 - track.format (string) : The format of the file

Otherwise, you can add songs to your device by using:

    mygear.add_song('Music/Europe/The_Final_Countdown.mp3')
    
You can obviously remove tracks with this function:
  
    mygear.remove_track(mygear.tracks[0])
    
    
# Examples:

With this example, you can add every musics in a directory to your Gear.

    os.chdir('Musics/Muse')
    for song in os.listdir('.'):
         mygear.add_track(song)
         
         
With this other example, you can remove every songs by ABBA from your Gear.

    for song in mygear.tracks:
        if song.artist == 'ABBA':
            print ('Removing "%s" '%song.title)
            mygear.remove_track(song)
