# ReelRatings: Movie and TV Show Ratings Aggregator

## Introduction
ReelRatings is a comprehensive movie ratings aggregator designed to provide users with a holistic view of movie and TV show ratings from multiple sources. Built with modern web technologies, this tool aims to simplify the process of finding reliable and aggregated ratings.

Live Demo: www.reelratingsdb.com

## Features
- **Search Functionality**: Users can search for a movie or TV show title.
- **Aggregated Data**: Upon selecting a title, the app fetches detailed information, including ratings, specific movie page URLs, box office figures, and stream availability.
- **Multiple Sources**: Data is sourced by scraping multiple websites, ensuring a well-rounded perspective on the selected title.

## Design Choices
During the development of ReelRatingsDB, several design choices were made to ensure efficiency and user-friendliness:

- **FAST API Framework**: A modern, high-speed web framework was chosen for its efficiency in building APIs using Python. FAST API which is optimal for asynchronous programming, and helped improve performance, getting data up to three times faster. 
- **BeautifulSoup for Web Scraping**: This Python library was selected for its robustness, reliabilty, and ease of use in scraping web content.
- **TMDB API**: The decision to use TMDB API was based on its comprehensive movie database and reliable data retrieval methods. Initially used OMDB API but the search was subpar in comparison.

## Conclusion
ReelRatingsDB was not just about building a tool for personal use; it was a profound learning experience. Through this project, various technologies were integrated, new skills were acquired, and a deeper understanding of software development was achieved. The goal is to continually improve and expand the features of ReelRatings, making it an invaluable tool for movie enthusiasts.

## Future Enhancements
- **Search Functionality**: Expand search functionality to title searches by director, actors, etc.
- **Database Integration**: Optimize performance and functionality with caching and storing information for quick retrieval 
- **User Experience**: Provide a continuous presentation of popular titles on the home page and add an account feature to save titles to a watch list

--- 

Disclaimer: This application is for demonstration purposes only and is not intended for commercial use. It utilizes data from the TMDb API and various third-party sources, but is not endorsed or certified by TMDb or any of the third-parties. All product and company names are trademarks™ or registered® trademarks of their respective holders. Use of them does not imply any affiliation with or endorsement by them.
