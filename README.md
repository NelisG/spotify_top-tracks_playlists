# Spotify top-tracks playlists
This repository contains the Python code to automatically create or update your top-tracks playlists. Top-tracks statistics are fetched from your [Last.fm](www.last.fm) account. These statistics are then used to update your Spotify playlists.

By default this code creates/updates the following three playlists on your Spotify account:
  * Top 10 | WEEK
  * Top 30 | MONTH
  * Top 50 | YEAR

## Usage

### Prerequisites

#### Packages
Have the required Python packages (Spotipy) installed on your Python environment using the following command:

```pip install -r requirements.txt```

#### Spotify API credentials
Fill in the Spotify API credentials in the main.py file. You can obtain these credentials by creating a Spotify developer account from https://developer.spotify.com. After creating an account, create a new application and copy the Client ID and Client Secret to the corresponding constants (`SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET`) in the main.py file.



### Running the script

```python main.py <Spotify_username> <Lastfm_username>```

The first time you run the script a link will be opened in your default browser to give the application access to modify your Spotify playlists with the scope "playlist-modify-public". After giving the application access, you are directed to a link starting with http://example.com/... Copy the whole link and paste it in the terminal or command prompt to give the script the necessary permissions. This will result in the generation or update of your top-tracks playlists.

## Automation (Linux)

It is recommended to make this script run at least once a week as your top-tracks change over time. On most Linux distributions it is common to do this using [Cron](https://en.wikipedia.org/wiki/Cron). An automated job is added to the crontab (the Cron table). It is important to note that Cron jobs are executed as Root and do not necessarily use the same Python version as the user-account. It is also important to note that your Spotify access token (which you obtained when you first ran the script) is stored in the same directory from where you ran the script. Therefore it is recommended to make a simple Bash script to ensure that the cronjob executes the Python script from the directory containing the access token. 

For example on a Raspberry Pi on which main.py is stored in /home/pi/spotify_playlists/

Make a simple bash script:

```bash
$ sudo nano /home/pi/spotify_playlists/automate.sh
```

Add the following lines:

``` 
cd /home/pi/spotify_playlists

/usr/bin/python main.py <spotify_username> <lastfm_username>
```

Open the Crontab in the terminal:

```$ crontab -e```

Add the Cron job at the end of the file:

```0 8 * * * bash /home/pi/spotify_playlists/automate.sh```

This code will run every day at 8 AM (if your device is online at that time). More information on the Crontab file is found in the [Crontab documentation](https://linux.die.net/man/5/crontab). 
