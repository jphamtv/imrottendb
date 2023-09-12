# ReelRatingsDB: Movie Ratings Aggregator

## Introduction
ReelRatingsDB is a comprehensive movie ratings aggregator designed to provide users with a holistic view of movie and TV show ratings from multiple sources. Built with modern web technologies, this tool aims to simplify the process of finding reliable and aggregated ratings.

## Features
- **Search Functionality**: Users can search for a movie or TV show title.
- **Aggregated Data**: Upon selecting a title, the app fetches detailed information, including ratings, specific movie page URLs, and box office figures.
- **Multiple Sources**: Data is sourced by scraping multiple websites, ensuring a well-rounded perspective on the selected title.

## Files and Descriptions
1. **main.py**: This is the main application file where the FAST API framework is implemented. It handles the primary functionality of the app, including API calls and data retrieval.
2. **tmdb.py**: This module is dedicated to handling interactions with the TMDB API. Contains functions that facilitate API calls to fetch movie and TV show details.
3. **scraper.py**: This script contains the web scraping techniques using the BeautifulSoup library. It's responsible for pulling data from various sources.
4. **app/static/**: This directory contains all the front-end files, including Images, CSS, and JavaScript files, which together with the HTML files, create the user interface of the application.
5. **app/templates/**: This directory contains all the HTML files for the web app.

## Design Choices
During the development of ReelRatingsDB, several design choices were made to ensure efficiency and user-friendliness:

- **FAST API Framework**: A modern, high-speed web framework was chosen for its efficiency in building APIs using Python. FAST API which is optimal for asynchronous programming, and helped improve performance, getting data up to three times faster. 
- **BeautifulSoup for Web Scraping**: This Python library was selected for its robustness, reliabilty, and ease of use in scraping web content.
- **TMDB API**: The decision to use TMDB API was based on its comprehensive movie database and reliable data retrieval methods. Initially used OMDB API but the search was subpar in comparison.

## Conclusion
ReelRatingsDB was not just about building a tool for personal use; it was a profound learning experience. Through this project, various technologies were integrated, new skills were acquired, and a deeper understanding of software development was achieved. The goal is to continually improve and expand the features of ReelRatingsDB, making it an invaluable tool for movie enthusiasts.

--- 

Disclaimer: This application is for demonstration purposes only and is not intended for commercial use. It utilizes data from the TMDb API and various third-party sources, but is not endorsed or certified by TMDb or any of the third-parties. All product and company names are trademarks™ or registered® trademarks of their respective holders. Use of them does not imply any affiliation with or endorsement by them.