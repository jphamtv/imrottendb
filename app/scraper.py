# scraping.py
import httpx
import logging

from bs4 import BeautifulSoup
from fastapi import HTTPException
from unidecode import unidecode


BASE_URLS = {
    "rottentomatoes": "https://www.rottentomatoes.com/search?search=",
    "letterboxd": "https://letterboxd.com/search/",
    "commonsensemedia": "https://www.commonsensemedia.org/search/",
    "imdb": "https://www.imdb.com/title/",
    "boxofficemojo": "https://www.boxofficemojo.com/title/",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64; rv:12.0) " "Gecko/20100101 Firefox/12.0"
    ),
    "Accept-Language": "en-US",
    "Accept-Encoding": "gzip, deflate",
    "Accept": "text/html",
    "Referer": "https://www.google.com",
}


async def make_request(url, headers=None):
    """
    Make an asynchronous HTTP GET request and parse the content with BeautifulSoup.

    Parameters:
    - url (str): The URL to request.
    - headers (dict, optional): Any HTTP headers to include in the request.

    Returns:
    - BeautifulSoup object: The HTML content of the response parsed by BeautifulSoup.

    Raises:
    - HTTPException: If the request fails or returns a non-2xx HTTP status code.

    """

    try:
        # Create an asynchronous HTTP client
        async with httpx.AsyncClient() as client:
            # Make the HTTP GET request
            response = await client.get(
                url, headers=headers, timeout=15, follow_redirects=True
            )

            # Check that the request was successful (status code 2xx)
            response.raise_for_status()

            # Parse the HTML content of the response with BeautifulSoup
            return BeautifulSoup(response.content, "html.parser")

    except httpx.RequestError as exc:
        # Log any exception specific to HTTPX
        logging.error(f"HTTPX Request Error: {exc}")

        # Raise a FastAPI HTTPException with a 500 status code
        raise HTTPException(status_code=500, detail="Internal Server Error")

    except Exception as generic_exc:
        # Log any other generic exceptions
        logging.error(f"Generic Exception: {generic_exc}")

        # Raise a FastAPI HTTPException with a 500 status code
        raise HTTPException(status_code=500, detail="Internal Server Error")


async def get_rottentomatoes_url(title, year, media_type):
    """Extract the RottenTomatoes URL for the title"""
    title = unidecode(title)
    year = year[:4]
    search_url = f"{BASE_URLS['rottentomatoes']}{title.replace(' ', '%20')}"
    soup = await make_request(search_url, HEADERS)
    search_result = soup.find(
        "search-page-media-row",
        {"releaseyear": {year}} if media_type == "Movie" else {"startyear": {year}},
    )

    if search_result:
        url_tag = search_result.find("a", {"data-qa": "thumbnail-link"})
        rottentomatoes_url = url_tag["href"]
        return rottentomatoes_url

    else:
        return None


async def get_letterboxd_url(title, year):
    """Extract the Letterboxd URL for the movie"""
    search_url = f"{BASE_URLS['letterboxd']}{title.replace(' ', '+')}/"
    soup = await make_request(search_url, HEADERS)
    search_results = soup.find_all("span", {"class": "film-title-wrapper"})

    for result in search_results:
        # Extract the text content
        year_element = result.find("small", class_="metadata")

        # If year matches, get the href from the parent <a> tag
        if year_element and year_element.text.strip() == year:
            href = result.find("a")["href"]

            return f"https://letterboxd.com{href}"

    return None


async def get_commonsense_info(title, year, media_type):
    """Extract the title's specific URL page and age rating"""
    search_url = f"{BASE_URLS['commonsensemedia']}{title.replace(' ', '%20')}"
    soup = await make_request(search_url, HEADERS)
    search_results = soup.find_all("div", {"class": "site-search-teaser"})

    for result in search_results:
        product_type_element = result.find("div", class_="review-product-type caption")
        product_type = (
            product_type_element.text.strip()
            if product_type_element is not None
            else None
        )

        if product_type != media_type.upper():
            continue

        # If year matches, get the href and age ratiing
        year_element = result.find("div", class_="review-product-summary")
        if year_element and year_element.text.strip()[-5:-1] != year:
            continue

        rating_age_element = result.find("span", {"class": "rating__age"})
        rating_age = (
            rating_age_element.text.strip() if rating_age_element is not None else None
        )
        if not rating_age:
            continue

        a_element = result.find("a")
        href = a_element["href"] if a_element is not None else None
        if not href:
            continue

        return {
            "url": f"https://www.commonsensemedia.org{href}",
            "rating": rating_age,
        }

    return None


async def get_imdb_rating(imdb_id):
    """Extract the average user rating"""
    if imdb_id:
        imdb_url = f"{BASE_URLS['imdb']}{imdb_id}"
        soup = await make_request(imdb_url, HEADERS)

        # Locate the class that contains the IMDb Rating
        rating = soup.find(
            "div", {"data-testid": "hero-rating-bar__aggregate-rating__score"}
        )

        return rating.text[:-3] if rating else None

    else:
        return None


async def get_boxofficemojo_url(imdb_id):
    boxofficemojo_url = f"{BASE_URLS['boxofficemojo']}{imdb_id}/"

    return boxofficemojo_url


async def get_box_office_amounts(imdb_id):
    """Extract box office amounts"""
    if imdb_id:
        url = f"{BASE_URLS['boxofficemojo']}{imdb_id}/"
        soup = await make_request(url, HEADERS)
        # Locate the span element that contains the Box Office amounts
        span_elements = soup.find_all("span", class_="a-size-medium a-text-bold")
        dollar_amounts = [span.get_text(strip=True) for span in span_elements]

        return dollar_amounts

    else:
        return None


async def get_justwatch_page(justwatch_url):
    """Extract the JustWatch page url for 'US'"""
    if justwatch_url:
        soup = await make_request(justwatch_url, HEADERS)

        try:
            link = soup.find("div", class_="homepage")
        except AttributeError:
            link = None

        return link.find("a")["href"] if link else None


async def get_rottentomatoes_scores(rottentomatoes_url):
    """Extract Tomotometer and Audience Scores"""
    if not rottentomatoes_url:
        return None

    soup = await make_request(rottentomatoes_url, HEADERS)
    # Get the element that contains the Tomatometer and Audience scores
    score_board = soup.find("score-board-deprecated")

    if not score_board:
        return None

    # Get the Tomatometer and Audience scores
    tomatometer = (
        score_board["tomatometerscore"] if score_board["tomatometerscore"] else None
    )
    audience_score = (
        score_board["audiencescore"] if score_board["audiencescore"] else None
    )

    return {
        "tomatometer": tomatometer,
        "tomatometer_state": score_board["tomatometerstate"],
        "audience_score": audience_score,
        "audience_state": score_board["audiencestate"],
    }


async def get_letterboxd_rating(letterboxd_url):
    """Extract the average user rating"""
    if not letterboxd_url:
        return None

    soup = await make_request(letterboxd_url, HEADERS)

    # Locate the class that contains the Tomatometer and Audience scores
    try:
        rating = soup.find("meta", {"name": "twitter:data2"}).get("content")
    except AttributeError:
        rating = None

    return round(float(rating[0:5]), 1) if rating else None
