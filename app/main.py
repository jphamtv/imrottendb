# main.py
import asyncio
import logging

from environs import Env
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .scraper import (
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
from starlette.middleware.sessions import SessionMiddleware
from .tmdb import get_title_details, search_title

# Initialize environment variables
env = Env()
env.read_env()

TMDB_API_KEY = env.str("TMDB_API_KEY")
SESSION_SECRET_KEY = env.str("SESSION_SECRET_KEY")

# Initialize FastAPI app
app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Initialize template engine
templates = Jinja2Templates(directory="app/templates")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logging.error(f"An HTTP exception occurred: {exc}")
    return templates.TemplateResponse(
        "500_error.html", {"request": request}, status_code=exc.status_code
    )


@app.exception_handler(Exception)
async def internal_server_error(request: Request, exc: Exception):
    logging.error(f"An error occurred: {exc}")
    return templates.TemplateResponse(
        "500_error.html", {"request": request}, status_code=500
    )


@app.get("/")
def index(request: Request):
    """Show home page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/search")
@app.post("/search")
def search(request: Request, title: str = Form(None)):
    """Search for a movie or TV show and display the results"""
    search_results = []

    try:
        if title:
            user_input = title.strip()
            if user_input:
                search_results = search_title(user_input)
    except Exception:
        raise HTTPException(status_code=500)

    return templates.TemplateResponse(
        "search.html",
        {
            "request": request,
            "search_results": search_results,
            "title": title,
        },
    )


@app.get("/details/{tmdb_id}/{media_type}/")
async def title_details(request: Request, tmdb_id: str, media_type: str):
    """Display detailed information and ratings for the selected title"""

    # Fetch title details
    details = get_title_details(tmdb_id, media_type, TMDB_API_KEY)
    title = details["title"]
    year = details["year"]
    imdb_id = details["imdb_id"]
    imdb_url = f"https://www.imdb.com/title/{imdb_id}"
    justwatch_url = details["justwatch_url"]

    # Movie specific tasks
    if media_type == "Movie":
        tasks = await execute_movie_tasks(
            imdb_id, title, year, media_type, justwatch_url
        )

    # TV show specific tasks
    elif media_type == "TV":
        tasks = await execute_tv_tasks(imdb_id, title, year, media_type, justwatch_url)

    return templates.TemplateResponse(
        "details.html",
        {
            "request": request,
            "details": details,
            "imdb_url": imdb_url,
            "media_type": media_type,
            **tasks,
        },
    )


async def execute_movie_tasks(
    imdb_id: str, title: str, year: str, media_type: str, justwatch_url: str
):
    """Execute asynchronous tasks specifically for movies."""
    # Initialize tasks
    boxofficemojo_url = asyncio.create_task(get_boxofficemojo_url(imdb_id))
    rottentomatoes_url = asyncio.create_task(
        get_rottentomatoes_url(title, year, media_type)
    )
    letterboxd_url = asyncio.create_task(get_letterboxd_url(title, year))
    justwatch_page = asyncio.create_task(get_justwatch_page(justwatch_url))
    box_office_amounts = asyncio.create_task(get_box_office_amounts(imdb_id))
    imdb_rating = asyncio.create_task(get_imdb_rating(imdb_id))
    commonsense_info = asyncio.create_task(get_commonsense_info(title, year))

    # Fetch scores immediately after URL is fetched
    rottentomatoes_url = await rottentomatoes_url
    rottentomatoes_scores = asyncio.create_task(
        get_rottentomatoes_scores(rottentomatoes_url)
    )

    # Fetch rating immediately after URL is fetched
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

    return {
        "imdb_rating": imdb_rating,
        "rottentomatoes_url": rottentomatoes_url,
        "rottentomatoes_scores": rottentomatoes_scores,
        "letterboxd_url": letterboxd_url,
        "letterboxd_rating": letterboxd_rating,
        "commonsense_info": commonsense_info,
        "boxofficemojo_url": boxofficemojo_url,
        "box_office_amounts": box_office_amounts,
        "justwatch_page": justwatch_page,
    }


async def execute_tv_tasks(
    imdb_id: str, title: str, year: str, media_type: str, justwatch_url: str
):
    """Execute asynchronous tasks specifically for TV shows."""
    # Initialize async tasks
    justwatch_page = asyncio.create_task(get_justwatch_page(justwatch_url))
    rottentomatoes_url = asyncio.create_task(
        get_rottentomatoes_url(title, year, media_type)
    )
    imdb_rating = asyncio.create_task(get_imdb_rating(imdb_id))
    commonsense_info = asyncio.create_task(get_commonsense_info(title, year))

    # Fetch scores immediately after URL is fetched
    rottentomatoes_url = await rottentomatoes_url
    rottentomatoes_scores = asyncio.create_task(
        get_rottentomatoes_scores(rottentomatoes_url)
    )

    # Await tasks
    imdb_rating = await imdb_rating
    commonsense_info = await commonsense_info
    justwatch_page = await justwatch_page if justwatch_url else None
    rottentomatoes_scores = await rottentomatoes_scores

    return {
        "imdb_rating": imdb_rating,
        "rottentomatoes_url": rottentomatoes_url,
        "rottentomatoes_scores": rottentomatoes_scores,
        "commonsense_info": commonsense_info,
        "justwatch_page": justwatch_page,
        "letterboxd_url": None,
        "letterboxd_rating": None,
        "boxofficemojo_url": None,
        "box_office_amounts": None,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
