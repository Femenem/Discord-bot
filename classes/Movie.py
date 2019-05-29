import requests # Http requests
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup # html parser

class Movie():
    """docstring for Movie."""

    def __init__(self, searchTitle):
        self.title = ""
        self.length = ""
        self.imdbRating = 0.0
        self.genres = []
        self.releaseDate = ""
        self.ageRating = ""
        self.summary = ""
        self.search_for_title(searchTitle)

    def search_for_title(self, title):
        url = "https://www.imdb.com/find?q="
        titles = title.split(' ')
        for title in titles:
            url += title + "+"
        try:
            with closing(requests.get(url, stream=True)) as resp:
                if self.is_good_response(resp):
                    html = BeautifulSoup(resp.content, 'html.parser')
                    count = 0
                    for result in html.find_all('tr', class_="findResult"):
                        count += 1
                        if 'TV Episode' in str(result):
                            continue
                        else: # First movie that isn't a tv series
                            link = result.find('a')
                            fullUrl = "https://www.imdb.com" + link['href']
                            self.scrape_title_data(fullUrl)
                            break

                    # print(html.find_all('tr', class_="findResult"))
                else:
                    print("Nothing here")

        except RequestException as e:
            self.log_error('Error during requests to {0} : {1}'.format(url, str(e)))
            return None

    def is_good_response(self, resp):
        """
        Returns True if the response seems to be HTML, False otherwise.
        """
        content_type = resp.headers['Content-Type'].lower()
        return (resp.status_code == 200
                and content_type is not None
                and content_type.find('html') > -1)

    def log_error(self, e):
        """
        It is always a good idea to log errors.
        This function just prints them, but you can
        make it do anything.
        """
        print(e)

    def scrape_title_data(self, url):
        try:
            with closing(requests.get(url, stream=True)) as resp:
                if self.is_good_response(resp):
                    html = BeautifulSoup(resp.content, 'html.parser')
                    infoBar = html.find('div', class_="title_bar_wrapper")
                    ## Searching for title and release date
                    title = infoBar.find('h1')
                    title = title.text
                    title = title.split("\xa0")
                    self.title = title[0]
                    self.releaseDate = title[0]

                    ## Searching for imdb rating
                    rating = infoBar.find('div', class_="ratingValue")
                    rating = rating.text[:-4] # Remove "/10 "
                    if(rating.startswith('\n')): # Sometimes starts with a \n
                        self.imdbRating = float(rating[1:]) # Remove \n
                    else:
                        self.imdbRating = float(rating)

                    ## Searching for film subtext (length, age rating, genres, release date)
                    subtext = infoBar.find('div', class_="subtext")
                    subvalues = []
                    for value in subtext.text.split("\n"):
                        value = value.strip()
                        if(value != '' and value != '\n' and value != '|'):
                            subvalues.append(value)
                    self.ageRating = subvalues[0]
                    self.length = subvalues[1]
                    stillGenres = True
                    genreNumber = 2 # starts after movie length
                    while stillGenres:
                        self.genres.append(subvalues[genreNumber])
                        if(subvalues[genreNumber+1][0].isdigit()):
                            genreNumber += 1
                            stillGenres = False
                            break
                        genreNumber += 1
                    self.releaseDate = subvalues[genreNumber]

                    ## Searching for summary
                    summary = html.find('div', class_="summary_text")
                    self.summary = summary.text.strip()

        except RequestException as e:
            self.log_error('Error during requests to {0} : {1}'.format(url, str(e)))
            return None

    def print_movie(self):
        string = "```"
        string += "Title: " + self.title + "\n"
        string += "Length: " + self.length + "\n"
        string += "IMDB Rating: " + str(self.imdbRating) + "\n"
        string += "Release Date: " + self.releaseDate + "\n"
        string += "Genres: "
        for genre in self.genres:
            string += genre + " "
        string += "\n"
        string += "Age Rating: " + self.ageRating + "\n"
        string += "Summary: " + self.summary + "\n"
        string += "```"
        return string
