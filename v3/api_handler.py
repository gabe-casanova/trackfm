import json
import os
import sys
import time
import requests
from tqdm import tqdm
from datetime import datetime, time as dt_time
from pathlib import Path
from ansi import ANSI

API_KEY:str = open('v3/admin/api_key.txt').read()        #  ** Replace with your API_KEY **
USER_AGENT:str = open('v3/admin/user_agent.txt').read()  #  ** Replace with your USER_AGENT **

# TODO-- fix bug with user_info/{USERNAME}.txt
#           figure out why it takes long to display tqdm
#           make it so if we've cached scrobs, then quickly incrememt bar vs instantly

USERNAME = ''
song_length_cache = {}


# =========== [1] Fetch Scrobbled Data: =====================================

def fetch_scrobbled_data(username):
    '''
    Handles the process of fetching all of the user's scrobbled data and 
    storing it in a seperate file located at /scrobbled_data/{username}.txt
    '''
    if username == '':
        # user ran 'python api_handler.py fetch' (prompt for username)
        while True:
            username = __get_username()
            if username.lower() == 'q':
                print()
                return
            if is_valid_user(username):
                break  # exit the while loop
            ANSI_USERNAME = ANSI.CYAN_BOLD + username + ANSI.RESET
            print(f'\n * Sorry, but {ANSI_USERNAME} is not a valid Last.fm '
                  'username')
    # if we get here, we have a valid Last.fm username
    global USERNAME
    USERNAME = username
    init_user_info_file()
    get_recent_tracks()
    print()


def init_user_info_file():
    '''
    Uses the contents of the user.getInfo API request to write to a text file 
    to be used later on during the fetchfm program
    '''
    LABELS = ['age', 'album_count', 'artist_count', 'country', 'gender', 
              'playcount', 'playlists', 'realname', 'subscriber',
              'track_count', 'url']
    response = lastfm_get({
        'method': 'user.getInfo',
        'user': USERNAME
    })
    if response is None:
        return  # early return
    # if we get here, we know the API request was successful
    j_user = response.json()['user']
    user_info = [j_user['age'], j_user['album_count'], j_user['artist_count'],
                 j_user['country'], j_user['gender'], j_user['playcount'],
                 j_user['playlists'], j_user['realname'], j_user['subscriber'],
                 j_user['track_count'], j_user['url']]
    # time to write to our user_info text file
    user_info = get_path('user_info', f'{USERNAME}.txt')
    with open(user_info, 'w') as f:
        # get the current datetime and format it
        current_datetime = datetime.now()
        formatted_date = current_datetime.strftime('%d %b %Y')
        twelve_hour_time = current_datetime.strftime('%I:%M %p')
        # timestamp file + append the user_info received via API call
        f.write(f'timestamp\t{formatted_date} {twelve_hour_time}\n')
        f.write(f'username\t{USERNAME}\n')
        for i, label in enumerate(LABELS):
            f.write(f'{label}\t{user_info[i]}\n')
    # write the current username to a text file in subdir user_info/
    current_user = get_path('user_info', 'current_user.txt')
    with open(current_user, 'w') as f:
        f.write(USERNAME)
    

def get_recent_tracks():
    '''
    Fetches all of the user's scrobbled data using the Last.fm API
    '''
    # Inform the user the fetching process is about to begin
    ansi_msg = (f'\n >> {ANSI.WHITE_UNDERLINED}Please hold tight as we fetch '
                f'{USERNAME}\'s data from Last.fm!{ANSI.RESET}\n')
    print(ansi_msg)
    # Create the desired txt file to store scrobbled data
    scrobbled_data = get_path('scrobbled_data', f'{USERNAME}.txt')
    Path(scrobbled_data).touch()
    # Begin process of fetching data from Last.fm
    last_saved_scrob = __get_last_saved_scrobble(scrobbled_data)
    reached_last_saved_scrob = False
    page = 1
    total_pages = __get_num_total_pages()
    prog_bar = tqdm(total=total_pages)
    while page <= total_pages and not reached_last_saved_scrob:
        prog_bar.update(1)
        payload = {
            'method': 'user.getRecentTracks',
            'limit': 200,
            'user': USERNAME,
            'page': page
        }
        response = lastfm_get(payload)
        if response is None:
            break
        # loop through the tracks listed on this page
        j_recenttracks = response.json()['recenttracks']
        reached_last_saved_scrob = __write_scrobs_to_file(j_recenttracks, 
                                                          last_saved_scrob)
        if reached_last_saved_scrob:
            # now combine the new scrobbles with the old scrobbles
            temp_file = get_path('scrobbled_data', 'temp.txt')
            with open(scrobbled_data, 'r') as f:
                old_scrobs = f.read()
            with open(temp_file, 'a') as f:
                f.write(old_scrobs)
            os.replace(temp_file, scrobbled_data)
        else:
            time.sleep(0.25)  # rate limit
            page += 1
    ''' end of while loop, terminate the progress bar '''
    if page != total_pages:
        # we were able to speed up the process by caching old scrobs
        prog_bar.update(total_pages - page)
    prog_bar.close()


def __get_username():
    ANSI_USER = ANSI.CYAN_BOLD + 'username' + ANSI.RESET
    ANSI_Q = ANSI.CYAN_BOLD + '`q`' + ANSI.RESET
    prompt = f'Provide your Last.fm {ANSI_USER}; to exit, type {ANSI_Q}: '
    print(f'\n{prompt}{ANSI.CYAN}', end='')
    user_input = input()
    print(ANSI.RESET, end='')  # resets ansi back to default
    return user_input


def __write_scrobs_to_file(j_recenttracks, last_saved_scrob):
    '''
    Helper function to gather the scrobbles from the current API request and
    write the data generated into a text file in the scrobbled_data/ subdir
    '''
    j_tracks = j_recenttracks['track']
    for track in j_tracks:
        album = track['album']['#text']
        artist = track['artist']['#text']
        song = track['name']
        date = track.get('date')  # check that this scrob contains 'date' key
        if date is not None:
            # disregards tracks that are currently being scrobbled
            date = date['#text']
            scrob = date + '\t' + artist + '\t' + album + '\t' + song
            if last_saved_scrob is None:
                # case 1: append scrobbles to user's txt file as expected
                scrobbled_data = get_path('scrobbled_data', f'{USERNAME}.txt')
                with open(scrobbled_data, 'a') as f:
                    f.write(f'{scrob}\n')   
            else:
                # case 2: append new scrobbles to a temp txt file until the
                #         current scrob equals the last_saved_scrob
                if scrob == last_saved_scrob:
                    return True
                temp_data = get_path('scrobbled_data', 'temp.txt')
                with open(temp_data, 'a') as f:
                    f.write(f'{scrob}\n')
    return False


def __get_num_total_pages():
    '''
    Returns the user's overall `totalPages` used to instantiate progress bar
    '''
    payload = {
        'method': 'user.getRecentTracks',
        'limit': 200,
        'user': USERNAME,
        'page': 1
    }
    response = lastfm_get(payload)
    if response is None:
        return -1
    j_recenttracks = response.json()['recenttracks']
    return int(j_recenttracks['@attr']['totalPages'])


def __get_last_saved_scrobble(scrobbled_data):
    '''
    In order to only make API calls for those scrobbles which we don't already
    have saved in the user's scrobbled_data txt file, let's save the 'last 
    saved scrobble' into a variable that way we can check if we've reached the
    point in the fetching process where we can stop making API calls since we
    have all the rest of the remaining data
    '''
    with open(scrobbled_data, 'r') as f:
        last_saved = f.readline().strip()
    if last_saved == '':
        return None
    # we assume that the read-in scrobble is formatted correctly
    return last_saved


# =========== [2] artist.getCorrection: =====================================

def fetch_artist_name_corrected(artist) -> tuple[str, bool]:
    '''
    Makes an API request to check if the supplied artist has a correction to a 
    canonical Last.fm artist
    -----
    Returns a tuple containing...
        - `str`: artist name (formatted correctly if found)
        - `bool`: indicates if the returned artist name is formatted correctly
    '''
    payload = {
        'method': 'artist.getCorrection',
        'artist': artist
    }
    response = lastfm_get(payload)
    if response is None:
        return artist, False
    # Now let's check if the JSON response actually contains desired fields
    j_res = response.json()
    if 'corrections' not in j_res or 'correction' not in j_res['corrections']:
        return artist, False
    # If we get here, we have a valid JSON response with desired fields
    formatted_artist = j_res['corrections']['correction']['artist']['name']
    return formatted_artist, True
    

# =========== [3] Fetch Song/Album Duration: ================================
    
def fetch_song_duration(song, artist, user) -> tuple[str, str, dt_time]:
    '''
    Makes an API request to retrieve the song length for the provided track.
    -----
    Returns a tuple containing...
        - `str`: song name (formatted correctly if found)
        - `str`: artist name (formatted correctly if found)
        - `dt_time`: track length (as a datetime.time object)
    '''
    # check the track length cache to see if we've made this request before
    if song_length_cache:
        for (cache_song, cache_artist), time_obj in song_length_cache.items():
            if (cache_song.lower() == song.lower() and
                    cache_artist.lower() == artist.lower()):
                # we found a match for the given request
                return cache_song, cache_artist, time_obj
    ''' if we get here, make an API request for a track we haven't cached '''
    j_response = fetch_song_metadata(song, artist, user)
    if j_response is None:
        return song, artist, None
    ''' if we get here, we know we have a valid json format '''
    duration = j_response['track']['duration']
    # store corrected names (without any misspellings) into cache dict
    retrieved_song = j_response['track']['name']
    retrieved_artist = j_response['track']['artist']['name']
    time_obj = __create_time_obj_from_milliseconds(duration)
    # store the successful track length info into the cache
    song_length_cache[(retrieved_song, retrieved_artist)] = time_obj
    return retrieved_song, retrieved_artist, time_obj
    

def fetch_album_duration(album, artist, user) -> tuple[str, str, dict, int]:
    '''
    Makes an API request to retrieve the album duration for the provided album.
    -----
    Returns a tuple containing...
        - `str`: album name (formatted correctly if found)
        - `str`: artist name (formatted correctly if found)
        - `dict`: track listings of the form {song_name: datetime.time obj}
        - `int`: user's playcount for the album
    '''
    j_response = fetch_album_metadata(album, artist, user)
    if j_response is None:
        return album, artist, None, 0
    ''' if we get here, we know we have a valid json format '''
    j_album = j_response['album']
    track_list = j_album['tracks']['track']  # python list
    result = {}
    for track in track_list:
        # find the duration of each track in the track list
        song_name = track['name']
        song_duration = 0 if track['duration'] is None else track['duration']
        result[song_name] = create_time_obj_from_seconds(song_duration)
    corrected_album = j_album['name']
    corrected_artist = j_album['artist']
    userplaycount = j_album['userplaycount']
    return corrected_album, corrected_artist, result, userplaycount


def create_time_obj_from_seconds(seconds):
    '''
    Returns a datetime.time object based on the provided amount of seconds
    '''
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return dt_time(int(hours), int(minutes), int(seconds))


def __create_time_obj_from_milliseconds(milliseconds):
    '''
    Returns a datetime.time object based on the provided milliseconds
    '''
    total_seconds = int(milliseconds) / 1000
    return create_time_obj_from_seconds(total_seconds)


# =========== [4] Fetch Song/Album Metadata: ================================

def fetch_song_metadata(song, artist, user):
    return __fetch_metadata('track.getInfo', song, artist, user)
    

def fetch_album_metadata(album, artist, user):
    return __fetch_metadata('album.getInfo', album, artist, user)


def __fetch_metadata(method, item, artist, user) -> json:
    '''
    Makes an API request to retrieve the Last.fm metadata for the given item; 
    currently item must either be a 'song' or 'album' name
    '''
    item_key = 'track' if method == 'track.getInfo' else 'album'
    formatted_artist = fetch_artist_name_corrected(artist)[0]
    payload = {
        'method': method,
        item_key: item,
        'artist': formatted_artist,
        'username': user,
        'autocorrect': True
    }
    response = lastfm_get(payload)
    if response is None or item_key not in response.json():
        return None
    return response.json()


# =========== [5] Utility: ==================================================
    
def lastfm_get(payload) -> requests:
    '''
    Generalized function for making a Last.fm API request
    '''
    # Define headers and URL
    headers = {'user-agent': USER_AGENT}
    url = 'https://ws.audioscrobbler.com/2.0/'
    # Add API key and format to the payload
    payload['api_key'] = API_KEY
    payload['format'] = 'json'
    # Generate the request
    response = requests.get(url, headers=headers, params=payload)
    if is_api_error(response):
        return None
    return response


def get_path(subdir, file) -> str:
    '''
    Returns the absolute path for a newly created file in the specified 
    subdirectory
    '''
    v3_path = os.path.dirname(__file__)
    subdir_path = os.path.join(v3_path, subdir)
    # If the subdirectory doesn't exist, create it dynamically
    if not os.path.exists(subdir_path):
        os.makedirs(subdir_path)
    return os.path.join(subdir_path, file)


def is_valid_user(username) -> bool:
    '''
    Returns a bool indicating if the given username is a valid Last.fm user
    '''
    payload = {
        'method': 'user.getInfo',
        'user': username
    }
    response = lastfm_get(payload)
    return False if response is None else True


def is_api_error(response):
    '''
    Returns a bool indicating if the API request was successful
    '''
    SUCCESS_STATUS_CODE = 200
    if response is None or response.status_code != SUCCESS_STATUS_CODE:
        return True
    return False


def get_ansi_bytey(ansi, aligned) -> list:
    '''
    Returns a list in which each element is a particular line of ansi Bytey
    '''
    if aligned:
        alignment = ['   ', '  ', '    ', '    ', '   ']
    else:
        alignment = ['', '', '', '', '']
    # construct bytey now
    BYTEY = [
        '_     /)---(\\' + alignment[0],
        '\\\\   (/ . . \\)' + alignment[1],
        ' \\\\__)-\\(*)/' + alignment[2],
        ' \\_       (_' + alignment[3],
        ' (___/-(____)' + alignment[4]
    ]
    ansi_bytey = [f'{ansi}{line}{ANSI.RESET}' for line in BYTEY]
    return ansi_bytey


def jprint(obj):
    '''
    Create a formatted string of the Python JSON object
    '''
    output = json.dumps(obj, sort_keys=True, indent=4)
    print(output)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'fetch':
        fetch_scrobbled_data('')
    