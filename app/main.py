# main.py
import asyncio
import time
from environs import Env

# Loads environment variables
env = Env()
env.read_env()

TMDB_API_KEY = env.str("TMDB_API_KEY")
SESSION_SECRET_KEY = env.str("SESSION_SECRET_KEY")

from scraper import (
    get_imdb_rating,
    get_rottentomatoes_url,
    get_rottentomatoes_scores,
    get_letterboxd_url,
    get_letterboxd_rating,
    get_commonsense_info,
    get_boxofficemojo_url,
    get_box_office_amounts,
    get_justwatch_page,
)
from tmdb import get_title_details, search_title

from fastapi import FastAPI, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()

app.add_middleware(
    SessionMiddleware, 
    secret_key=SESSION_SECRET_KEY, 
    max_age=None
)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/")
def index(request: Request):
    """Show home page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/search")
@app.post("/search")
def search(request: Request, title: str = Form(None)):
    """Search for a movie or tv show and show the results"""
    session = request.session
    search_results = []

    # Fetch movie and TV shows if title is valid
    if title:
        user_input = title.strip()
        if user_input:
            # Get results via TMDB API
            search_results = search_title(user_input)
            # Store the results in session
            session["search_results"] = search_results

    elif "search_results" in session:
        # Use session when going back via "Back to Results" button
        search_results = session["search_results"]

    return templates.TemplateResponse("search.html", {
        "request": request, 
        "search_results": search_results,
    })


@app.get("/details/{tmdb_id}/{media_type}/")
async def title_details(request: Request, tmdb_id: str, media_type: str):
    """Show selected title details"""
    
    # Start timer
    start_time0 = time.time()

    # Fetch title details from TBMD API 
    details = get_title_details(tmdb_id, media_type, TMDB_API_KEY)
    title = details["title"]
    year = details["year"]
    imdb_id = details["imdb_id"]
    imdb_url = f"https://www.imdb.com/title/{imdb_id}"
    justwatch_url = details["justwatch_url"]

    # Movie specific tasks
    if media_type == "Movie":

        # Initialize async tasks
        boxofficemojo_url = asyncio.create_task(get_boxofficemojo_url(imdb_id)) 
        rottentomatoes_url = asyncio.create_task(get_rottentomatoes_url(title, year, media_type))
        letterboxd_url = asyncio.create_task(get_letterboxd_url(title, year))
        justwatch_page = asyncio.create_task(get_justwatch_page(justwatch_url))
        box_office_amounts = asyncio.create_task(get_box_office_amounts(imdb_id)) 
        imdb_rating = asyncio.create_task(get_imdb_rating(imdb_id))
        commonsense_info = asyncio.create_task(get_commonsense_info(title, year))

        # Await Rottentomatoes task and fetch scores immediately after URL is fetched
        rottentomatoes_url = await rottentomatoes_url
        rottentomatoes_scores = asyncio.create_task(get_rottentomatoes_scores(rottentomatoes_url))

        # Await Letterboxd URL task and fetch rating immediately after URL is fetched
        letterboxd_url = await letterboxd_url
        letterboxd_rating = asyncio.create_task(get_letterboxd_rating(letterboxd_url))
        
        # Await tasks
        imdb_rating = await imdb_rating
        boxofficemojo_url = await boxofficemojo_url
        box_office_amounts = await box_office_amounts
        commonsense_info = await commonsense_info
        justwatch_page = await justwatch_page if justwatch_url else None
        rottentomatoes_scores = await rottentomatoes_scores
        letterboxd_rating = await letterboxd_rating

    # TV show specific tasks
    elif media_type == "TV":

        # Initialize async tasks
        justwatch_page = asyncio.create_task(get_justwatch_page(justwatch_url))
        rottentomatoes_url = asyncio.create_task(get_rottentomatoes_url(title, year, media_type))
        imdb_rating = asyncio.create_task(get_imdb_rating(imdb_id))   
        commonsense_info = asyncio.create_task(get_commonsense_info(title, year))

        # Await Rottentomatoes task and fetch scores immediately after URL is fetched
        rottentomatoes_url = await rottentomatoes_url
        rottentomatoes_scores = asyncio.create_task(get_rottentomatoes_scores(rottentomatoes_url))

        # Await tasks
        imdb_rating = await imdb_rating
        commonsense_info = await commonsense_info
        justwatch_page = await justwatch_page if justwatch_url else None
        rottentomatoes_scores = await rottentomatoes_scores

        # Set variables to 'None' so they don't display on the page
        letterboxd_url = None
        letterboxd_rating = None
        boxofficemojo_url = None
        box_office_amounts = None

    # End timer and return total
    end_time0 = time.time()
    execution_time0 = end_time0 - start_time0
    print(f"Total: {execution_time0}")

    return templates.TemplateResponse("details.html", {
        "request": request,
        "details": details,
        "imdb_url": imdb_url,
        "imdb_rating": imdb_rating,
        "media_type": media_type,
        "rottentomatoes_url": rottentomatoes_url,
        "rottentomatoes_scores": rottentomatoes_scores,
        "letterboxd_url": letterboxd_url,
        "letterboxd_rating": letterboxd_rating,
        "commonsense_info": commonsense_info,
        "boxofficemojo_url": boxofficemojo_url,
        "box_office_amounts": box_office_amounts,
        "justwatch_page": justwatch_page,   
    })


@app.get("/loading/")
async def loading(request: Request):
    return templates.TemplateResponse("loading.html", {"request": request})
