# _Deprecated_
Check out the _slightly_ more polished version of this functionality [here](https://lastfm2wrapped.herokuapp.com/app/), with code [here](https://github.com/ashtonmoomoo/lastfm2wrapped).

# wrapped_generator
Generate a "Spotify Wrapped" playlist for a given year using historic Last.fm data.

To use this program you will need a Last.fm account with data from before you Spotify introduced Wrapped (2016). You will also need to have [api keys for Spotify](https://developer.spotify.com/dashboard/applications), which this program expects to find in your environment variables.

There's always the chance that your Last.fm listening data may not map perfectly onto Spotify tracks. Tracks which were not able to added to the playlist are logged in standard output so you can choose how to proceed.

## Usage
1. Ensure you have the relevant environment variables set
2. Download `wrapped_generator.py` into some directory
3. `cd` to the directory in a terminal
4. Do `python3 wrapped_generator.py year`
5. Check Spotify

This is pretty quick and dirty so feedback is welcomed.
