import requests # Http requests
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup # html parser
import sqlite3

class Movie():
    """docstring for Movie."""

    def __init__(self, searchTitle):
        self.imdbID = ""
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
                        elif 'TV Series' in str(result):
                            continue
                        else: # First movie that isn't a tv series
                            link = result.find('a')
                            self.imdbID = link['href'][7:-1]
                            values = self.check_movie_in_database(self.imdbID) # Check if values are in database
                            if(values != None):
                                print("Loading movie from database")
                                self.load_movie_from_database(values)
                                break
                            else:
                                print("Scraping movie from IMDB")
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

                    self.save_to_database()

        except RequestException as e:
            self.log_error('Error during requests to {0} : {1}'.format(url, str(e)))
            return None

    def save_to_database(self):
        with sqlite3.connect('data/movies.db') as db:
            c = db.cursor()
            genres = ""
            for genre in self.genres:
                genres += genre + " "
            data = [self.imdbID, self.title, self.length, self.imdbRating, genres, self.releaseDate, self.ageRating, self.summary]
            c.execute('''INSERT INTO Movies
            (IMDBID, Title, Length, Rating, Genres, ReleaseDate, AgeRating, Summary)
            values(?,?,?,?,?,?,?,?);
            ''', data)
            db.commit()

    def load_movie_from_database(self, values):
        self.imdbID = values[1]
        self.title = values[2]
        self.length = values[3]
        self.imdbRating = values[4]
        self.releaseDate = values[5]
        for genre in values[6].split(" "):
            self.genres.append(genre)
        self.ageRating = values[7]
        self.summary = values[8]

    def check_movie_in_database(self, id):
        id = (id,)
        with sqlite3.connect('data/movies.db') as db:
            c = db.cursor()
            c.execute('SELECT * FROM Movies WHERE IMDBID=?', id)
            return c.fetchone()

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
