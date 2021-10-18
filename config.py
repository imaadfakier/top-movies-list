import os

# --- the movie database
os.environ['TMDB_API_KEY'] = 'enter api key'
TMDB_API_KEY = os.environ.get(key='TMDB_API_KEY')

os.environ['TMDB_BEARER_TOKEN'] = 'enter bearer token'
TMDB_BEARER_TOKEN = os.environ.get(key='TMDB_BEARER_TOKEN')
