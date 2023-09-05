# scraping.py
import httpx

from bs4 import BeautifulSoup
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
        "Mozilla/5.0 (X11; Linux x86_64; rv:12.0) "
        "Gecko/20100101 Firefox/12.0"
    ),
    "Accept-Language": "en-US",
    "Accept-Encoding": "gzip, deflate",
    "Accept": "text/html",
    "Referer": "https://www.google.com"
}


async def make_request(url, headers=None):
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, timeout=10, follow_redirects=True)

        return BeautifulSoup(response.content, "html.parser")


async def get_rottentomatoes_url(title, year, media_type):
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


async def get_commonsense_info(title, year):
    search_url = f"{BASE_URLS['commonsensemedia']}{title.replace(' ', '%20')}"
    soup = await make_request(search_url, HEADERS)
    search_results = soup.find_all("div", {"class": "site-search-teaser"})

    for result in search_results:
        year_element = result.find("div", class_="review-product-summary")

        # If year matches, get the href from the parent <a> tag
        if year_element and year_element.text.strip()[-5:-1] == year:
            href = result.find("a")["href"]
            rating_age = result.find("span", {"class": "rating__age"}).text.strip()

            return {
                "url": f"https://www.commonsensemedia.org{href}",
                "rating": rating_age,
            }
        
    return None


async def get_imdb_rating(imdb_id):
    imdb_url = f"{BASE_URLS['imdb']}{imdb_id}"
    soup = await make_request(imdb_url, HEADERS)

    # Locate the class that contains the IMDb Rating
    rating = soup.find(
        "div", {"data-testid": "hero-rating-bar__aggregate-rating__score"}
    )

    return rating.text[:-3] if rating else None


async def get_boxofficemojo_url(imdb_id):
    boxofficemojo_url = f"{BASE_URLS['boxofficemojo']}{imdb_id}/"
    
    return boxofficemojo_url


async def get_box_office_amounts(imdb_id):
    url = f"{BASE_URLS['boxofficemojo']}{imdb_id}/"
    soup = await make_request(url, HEADERS)
    # Locate the span element that contains the Box Office amounts
    span_elements = soup.find_all("span", class_="a-size-medium a-text-bold")
    dollar_amounts = [span.get_text(strip=True) for span in span_elements]

    return dollar_amounts


async def get_justwatch_page(justwatch_url):
    """Get the JustWatch page url for 'US'"""
    if justwatch_url:
        soup = await make_request(justwatch_url, HEADERS)

        try:
            link = soup.find('div', class_='homepage')
        except AttributeError:
            link = None

        return link.find('a')['href'] if link else None


async def get_rottentomatoes_scores(rottentomatoes_url):
    if not rottentomatoes_url:
        return None
    
    soup = await make_request(rottentomatoes_url, HEADERS)
    # Get the element that contains the Tomatometer and Audience scores
    score_board = soup.find("score-board")

    if not score_board:
        return None
    
    # Get the Tomatometer and Audience scores, append '%' for display purposes
    tomatometer = (
        f'{score_board["tomatometerscore"]}%'
        if score_board["tomatometerscore"]
        else None
    )
    audience_score = (
        f'{score_board["audiencescore"]}%' if score_board["audiencescore"] else None
    )

    return {
        "tomatometer": tomatometer,
        "tomatometer_state": score_board["tomatometerstate"],
        "audience_score": audience_score,
        "audience_state": score_board["audiencestate"],
    }


async def get_letterboxd_rating(letterboxd_url):
    if not letterboxd_url:
        return None
    
    soup = await make_request(letterboxd_url, HEADERS)

    # Locate the class that contains the Tomatometer and Audience scores
    try:
        rating = soup.find("meta", {"name": "twitter:data2"}).get("content")
    except AttributeError:
        rating = None

    return round(float(rating[0:5]), 1) if rating else None