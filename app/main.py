# main.py
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
    get_letterbxd_url,
    get_letterbxd_rating,
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

    # Search for movie or TV show titles
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

    return templates.TemplateResponse("search.html", {"request": request, "search_results": search_results})


@app.get("/details/{tmdb_id}/{media_type}/")
async def title_details(request: Request, tmdb_id: str, media_type: str):
    """Show selected title details"""
    details = get_title_details(tmdb_id, media_type, TMDB_API_KEY)
    title = details["title"]
    year = details["year"]
    imdb_id = details["imdb_id"]
    imdb_url = f"https://www.imdb.com/title/{imdb_id}"
    justwatch_url = details["justwatch_url"]

    imdb_rating = get_imdb_rating(imdb_id)
    rottentomatoes_url = get_rottentomatoes_url(title, year, media_type)
    rottentomatoes_scores = get_rottentomatoes_scores(rottentomatoes_url)
    commonsense_info = get_commonsense_info(title, year)

    if justwatch_url:
        justwatch_page = get_justwatch_page(justwatch_url)
    else:
        justwatch_page = None

    if media_type == "Movie":
        letterbxd_url = get_letterbxd_url(title, year)
        letterbxd_rating = get_letterbxd_rating(letterbxd_url)
        boxofficemojo_url = get_boxofficemojo_url(imdb_id)
        box_office_amounts = get_box_office_amounts(boxofficemojo_url)
    elif media_type == "TV":
        letterbxd_url = None
        letterbxd_rating = None
        boxofficemojo_url = None
        box_office_amounts = None
    return templates.TemplateResponse(
        "details.html", {
        "request": request,
        "details": details,
        "imdb_url": imdb_url,
        "imdb_rating": imdb_rating,
        "media_type": media_type,
        "rottentomatoes_url": rottentomatoes_url,
        "rottentomatoes_scores": rottentomatoes_scores,
        "letterbxd_url": letterbxd_url,
        "letterbxd_rating": letterbxd_rating,
        "commonsense_info": commonsense_info,
        "boxofficemojo_url": boxofficemojo_url,
        "box_office_amounts": box_office_amounts,
        "justwatch_page": justwatch_page,   
    })


# start_time = time.time()
# # Test how long to run
# end_time = time.time()
# execution_time = end_time - start_time
# print()
# print(f"Total: {execution_time}")
# print()
