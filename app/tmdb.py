# search.py
import requests

from environs import Env
from utils import format_runtime

# Loads environment variables
env = Env()
env.read_env()

# Gets the TMDB API key from the environment variables
TMDB_API_KEY = env.str("TMDB_API_KEY")


# --------- SEARCH FOR MOVIE OR TV SERIES -------------- #

def search_title(user_input):
    """Look up movie, TV shows, and people using the TMDB API"""
    title = user_input.replace(" ", "%20")
    url = f"https://api.themoviedb.org/3/search/multi?api_key={TMDB_API_KEY}&query={title}&include_adult=false&language=en-US&page=1"
    search_results = get_search_results(url)
    filtered_results = filter_search_results(search_results)

    return filtered_results


def get_search_results(url):
    # Call API and get JSON data
    response = requests.get(url)
    response.raise_for_status()

    return response.json()


def filter_search_results(search_results):
    """Filter the search results based on media type"""
    poster_base_url = "https://www.themoviedb.org/t/p/w185"
    seen_tmdb_ids = set()
    filtered_results = []

    for result in search_results["results"]:
        tmdb_id = result.get("id")
        poster_path = result.get("poster_path")
        media_type = result.get("media_type")
        poster_img = get_poster_image(poster_base_url, poster_path)

        # Check if TMDB id is already seen to avoid duplicates
        if tmdb_id not in seen_tmdb_ids:
            seen_tmdb_ids.add(tmdb_id)
            filtered_result = get_filtered_results(
                result, media_type, tmdb_id, poster_img
            )

            if filtered_result:
                filtered_results.append(filtered_result)

    return filtered_results


def get_poster_image(poster_base_url, poster_path):
    # Use image placeholder if no poster file path exists
    if poster_path is None:
        return "/static/img/poster-holder.jpg"
    else:
        return f"{poster_base_url}{poster_path}"


def get_filtered_results(result, media_type, tmdb_id, poster_img):
    """Get the filtered result based on media type"""
    if media_type == "movie":
        return {
            "tmdb_id": tmdb_id,
            "title": result.get("title"),
            "year": result.get("release_date")[0:4],
            "media_type": media_type.title(),
            "poster_img": poster_img,
        }
    
    elif media_type == "tv":
        return {
            "tmdb_id": tmdb_id,
            "title": result.get("name"),
            "year": result.get("first_air_date")[0:4],
            "media_type": media_type.upper(),
            "poster_img": poster_img,
        }


# --------- SEARCH TITLE DETAILS -------------- #

def get_media_details(tmdb_id, media_type, TMDB_API_KEY):
    """Fetch the details of the selected title details using the TMDB API"""
    url = f"https://api.themoviedb.org/3/{media_type.lower()}/{tmdb_id}?api_key={TMDB_API_KEY}&language=en-US&append_to_response=release_dates,watch/providers,external_ids,credits"
    response = requests.get(url)
    response.raise_for_status()

    return response.json()


def get_common_details(media_details):
    """Extract common details for both Movie and TV series"""
    poster_path = media_details.get("poster_path")
    poster_img = (
        f"https://image.tmdb.org/t/p/w500{poster_path}"
        if poster_path
        else "/static/img/poster-holder.jpg"
    )
    justwatch_url = get_justwatch_url(media_details)

    return poster_img, justwatch_url


def get_runtime(media_details):
    """Get runtime and format it"""
    runtime = media_details.get("runtime")

    return format_runtime(runtime) if runtime else None


def get_movie_details(media_details):
    """Extract details specific to Movie"""
    imdb_id = media_details.get("imdb_id")
    title = media_details.get("title")
    year = media_details.get("release_date")[0:4]
    runtime = get_runtime(media_details) or None
    director = get_director(media_details) or None
    certification = get_certification(media_details) or None

    return imdb_id, title, year, runtime, director, certification


def get_tv_details(media_details):
    """Extract details specific to TV"""
    imdb_id = media_details.get("external_ids")["imdb_id"]
    title = media_details.get("name")
    year = media_details.get("first_air_date")[0:4]
    creator = get_creator(media_details) or None

    return imdb_id, title, year, creator


def get_director(media_details):
    """Get director(s) for movies"""
    movie_crew = media_details.get("credits", {}).get("crew", [])

    return [item.get("name") for item in movie_crew if item["job"] == "Director"]


def get_creator(media_details):
    """Get creator(s) for TV series"""
    return [item.get("name") for item in media_details.get("created_by", [])]


def get_certification(media_details):
    """Get movie certification rating for 'US'"""
    release_results = media_details.get("release_dates", {}).get("results", [])

    for result in release_results:
        if result["iso_3166_1"] == "US":
            for release_date in result["release_dates"]:
                certification = release_date["certification"]

                if certification:

                    return certification
                
    return None


def get_justwatch_url(media_details):
    """Get the URL for the title's JustWatch TMDB page for 'US'"""
    providers = media_details.get("watch/providers", {}).get("results")

    try:
        justwatch_url = providers["US"]["link"]
    except KeyError:
        justwatch_url = None

    return justwatch_url


def get_title_details(tmdb_id, media_type, TMDB_API_KEY):
    """Get the details for the selected title and media type"""
    media_details = get_media_details(tmdb_id, media_type, TMDB_API_KEY)
    poster_img, justwatch_url = get_common_details(media_details)

    if media_type == "Movie":
        imdb_id, title, year, runtime, director, certification = get_movie_details(
            media_details
        )
        filtered_details = {
            "director": director,
            "imdb_id": imdb_id,
            "media_type": media_type,
            "title": title,
            "year": year,
            "runtime": runtime,
            "certifcation": certification,
            "poster_img": poster_img,
            "justwatch_url": justwatch_url,
        }

    elif media_type == "TV":
        imdb_id, title, year, creator = get_tv_details(media_details)
        filtered_details = {
            "creator": creator,
            "imdb_id": imdb_id,
            "media_type": media_type,
            "title": title,
            "year": year,
            "poster_img": poster_img,
            "justwatch_url": justwatch_url,
        }

    return filtered_details