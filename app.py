
# ---------------------------------------------------------import Files---------------------------------------------------
# importing required APIs and pachages
from string import punctuation
from flask import Flask, render_template, request, url_for, redirect, session
import requests
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import mysql.connector
import tmdbsimple as tmdb
import requests
from werkzeug.wrappers import Request, Response
import os
from flask_sqlalchemy import SQLAlchemy


# -------------------------------------------------------------------------------------------------------------------------

app = Flask(__name__)

mysql_host= os.environ.get('DB_HOST')
mysql_user= os.environ.get('DB_USER') 
mysql_password=  os.environ.get('DB_PASSWORD') 
mysql_port= os.environ.get('DB_PORT')
mysql_db= os.environ.get('DB_NAME') 

# ---------------------------------------------------------Movie Recommondation--------------------------------------------


# TMDb API key 
tmdb.API_KEY = '4ea0432fe4d2e57ddd43b5aee68d817b'
API_KEY = '4ea0432fe4d2e57ddd43b5aee68d817b'


# given the name of the movie, gives the genres (category) of the movie
# @param name_of_the_movie --> takes the name of the movie
# @return Genres of the movie name given
# Function to get genres of a movie by its name using TMDb API
def get_genres(name_of_the_movie: str):
    # Search for the movie by name
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={name_of_the_movie}"
    response = requests.get(search_url)
    data = response.json()

    # If no movie found or error in API response, return None
    if not data['results']:
        return None

    movie_id = data['results'][0]['id']

    # Get details of the movie by its ID
    movie_details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"
    response = requests.get(movie_details_url)
    details = response.json()

    # Get genres of the movie
    genres = [genre['name'] for genre in details['genres']]

    return genres


# Function to get top 10 recommended movies by genres using TMDb API
def get_recommended(genres: str):
    # Get genre IDs
    genre_ids = ','.join([str(genre_id) for genre_id in get_genre_ids(genres)])

    # Get top rated movies by specified genres, sorted by popularity
    discover_url = f"https://api.themoviedb.org/3/discover/movie?api_key={API_KEY}&sort_by=popularity.desc&with_genres={genre_ids}"
    response = requests.get(discover_url)
    data = response.json()

    # Extract top 10 movie titles
    top_10_movies = [movie['title'] for movie in data['results'][:10]]

    return top_10_movies


def get_genre_ids(genres: str):
    genre_ids = {
        'comedy': 35,
        'romance': 10749,
        'drama': 18,
        'animation': 16,
        'science fiction': 878,
        'action': 28,
        'mystery': 9648,
        'adventure': 12,
        'horror': 27,
        'crime': 80,
        'fantasy': 14
    }
    return [genre_ids[genre.strip().lower()] for genre in genres.split(',') if genre.strip().lower() in genre_ids]



# checks for the most watched genres
# @param list_of_movies: list of watched movies by name
# @return recommended list of movies
def get_recommended_list(list_of_movies):
    genre_list = []
    genres = ['Comedy', 'Romance', 'Drama', 'Animation', 'Science Fiction', 'Action',
              'Mystery', 'Adventure', 'Horror', 'Crime', 'Fantasy']
    number_of_appearances = [0] * len(genres)

    for movie_title in list_of_movies:
        genre = get_genres(movie_title)
        if genre:
            genre_list.extend(genre)  # extend instead of append to flatten the genre_list
    # Count the number of appearances of each genre
    for genre in genre_list:
        if genre in genres:
            index = genres.index(genre)
            number_of_appearances[index] += 1
        
    # Find the genre with the maximum number of appearances
    max_index = number_of_appearances.index(max(number_of_appearances))
    most_common_genre = genres[max_index]
    
    return get_recommended(most_common_genre)


# this function takes the movie title and returns its rating 
# @param movive title
# @return the rating in float  
def get_movie_rating(movie_title):
    search = tmdb.Search()
    response = search.movie(query=movie_title)
    if len(search.results) > 0:
        movie_id = search.results[0]['id']
        movie = tmdb.Movies(movie_id)
        response = movie.info()
        rating = movie.vote_average if hasattr(movie, 'vote_average') else 'N/A'
        return rating
    else:
        return 'N/A'

# -------------------------------------------------------------------------------------------------------------------------



# ---------------------------------------------------------Youtube Api----------------------------------------------------
# Find trailer using youtube API
def find_trailer(name):
    api_key_Y1 = os.environ.get('api_key_Y1')
    api_key_Y2 = os.environ.get('api_key_Y2')
    api_keys = [api_key_Y1 , api_key_Y2]  # Add your API keys here

    for api_key in api_keys:
        search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={name}+trailer&type=video&key={api_key}"
        response = requests.get(search_url)
        data = response.json()
        print("API {api_key} tested")
        if data.get("items"):
            video_id = data["items"][0]["id"]["videoId"]
            link = "https://www.youtube.com/embed/" + video_id
            return link
    print("No video found.")
    return "https://www.youtube.com/embed/GFq6wH5JR2A"

# ---------------------------------------------------------Flask----------------------------------------------------


@app.route('/', methods=['GET', 'POST'])
def WelcomeScreen():
    return render_template('WelcomeScreen.html')

@app.route('/login', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if ifExist(username):
            if if_Password_is_right(username,password):
                global UserName 
                UserName = username
                return redirect('/success')
        else:
            return render_template('LoginScreen.html')
    return render_template('LoginScreen.html')


@app.route('/SignUp', methods=['GET', 'POST'])
def SignUp():
    if request.method == 'POST':
        if 'username' in request.form and 'password' in request.form and 'ConfirmPassword' in request.form:
            username = request.form['username']
            password = request.form['password']
            ConfirmPassword = request.form['ConfirmPassword']
            if password == ConfirmPassword and not ifExist(username):
                add(username,password)
                return render_template('LoginScreen.html')
            else:
                return render_template('SignUpScreen.html')
        else:
            return render_template('SignUpScreen.html')
    else:
            return render_template('SignUpScreen.html')
        


# Example usage:


@app.route('/success', methods=['GET', 'POST'])
def success():
    global counter
    counter = 0
    
    if len( Movie_list(UserName)) == 0:
        recommended_list = get_recommended('Drama')
        name = recommended_list[counter]
        genres = get_genres(name)
        youtube = find_trailer(name)
        rate = get_movie_rating(name)
    else:
        recommended_list = get_recommended_list(Movie_list(UserName))
        name = recommended_list[counter]
        genres = get_genres(name)
        youtube = find_trailer(name)
        rate = get_movie_rating(name)
    if request.method == 'POST':
        MovieInsert1 = request.form['MovieInsert']
        add_movie(UserName, MovieInsert1)
        recommended_list = get_recommended_list(Movie_list(UserName))
        name = recommended_list[counter]
        genres = get_genres(name)
        youtube = find_trailer(name)
        rate = get_movie_rating(name)
        return render_template('MovieRecommender.html', movie_list = Movie_list(UserName), youtube = youtube, genres = genres, name = name, rate = rate )
    return render_template('MovieRecommender.html', movie_list = Movie_list(UserName), youtube = youtube, genres = genres, name = name, rate = rate )



@app.route('/next', methods=['GET', 'POST'])
def nextMovie():
    global counter
    
    if request.method == 'POST':
        if len( Movie_list(UserName)) == 1:
            recommended_list = get_recommended('Drama')
            counter = (counter + 1) % 10  # Ensures counter loops back to 0 when it reaches 11
            name = recommended_list[counter]
            genres = get_genres(name)
            youtube = find_trailer(name)
            rate = get_movie_rating(name)
        else:
            recommended_list = get_recommended_list(Movie_list(UserName))
            counter = (counter + 1) % 10  # Ensures counter loops back to 0 when it reaches 11
            name = recommended_list[counter]
            genres = get_genres(name)
            youtube = find_trailer(name)
            rate = get_movie_rating(name)
        return render_template('MovieRecommender.html', movie_list = Movie_list(UserName), youtube = youtube, genres = genres, name = name, rate = rate )
    return render_template('MovieRecommender.html', movie_list = Movie_list(UserName), youtube = youtube, genres = genres, name = name, rate = rate )



# ------------------------------------------------MYSQL-------------------------------------------------------

# Verify the environment variables are loaded correctly
print(f"Host: {mysql_host}, User: {mysql_user}, Password: {mysql_password}, Port: {mysql_port}, DB: {mysql_db}")

# Function to connect to the database
def get_db_connection():
    # MySQL configurations
    db_config = {
        'host': os.environ.get('DB_HOST'),
        'database': os.environ.get('DB_NAME'),
        'user': os.environ.get('DB_USER'),
        'password': os.environ.get('DB_PASSWORD'),
        'port': 3306  # Default port is 3306
    }
    attempts = 10
    for attempt in range(1, attempts + 1):
        try:
            conn = mysql.connector.connect(**db_config)
            return conn
        except mysql.connector.Error as err:
            print(f"Attempt {attempt} to connect to the database failed: {err}")
            if attempt == attempts:
                print(f"Unable to connect to the database after {attempts} attempts.")
                return None

## regester the username and password to the database
def add(username,password):
    mydb = get_db_connection()
    mycursor = mydb.cursor()
    sql = "INSERT INTO user (Username, Password, Movies) VALUES (%s, %s, %s)"
    val = (username, password," ")
    mycursor.execute(sql, val)
    mydb.commit()
    mycursor.execute("SELECT * FROM user")
    for x in mycursor:
        print(x)
    mycursor.close()
    mydb.close



## Checking if the name is in the data base
def ifExist(username):
    # Connect to the database
    mydb = get_db_connection()

    # Create a cursor object
    mycursor = mydb.cursor()

    # Query the database
    mycursor.execute("SELECT * FROM user WHERE Username = %s", (username,))

    # Fetch all the results of the query
    result = mycursor.fetchall()

    return result


## Checking if the name is in the data base
def if_Password_is_right(username, password):
    # Connect to the database
    mydb = get_db_connection()
    try:
        with mydb.cursor() as cursor:
            # Execute the SELECT statement to retrieve the stored password for the given username
            sql = "SELECT Password FROM user WHERE Username = %s"
            cursor.execute(sql, (username,))
            result = cursor.fetchone()
            if result is not None:  # Check if result is not None
                # Compare the stored password to the input password
                if result[0] == password:  # Access password using index 0
                    print("Password match.")
                    return True
            print("Password does not match or user not found.")
            return False
    finally:
        mydb.close()


# add function that add a movie to the list of movies for every user
def add_movie(username, movie):
    cnx = get_db_connection()
    cursor = cnx.cursor()
    query = "SELECT Movies FROM user WHERE username = '"+username+"'"
    cursor.execute(query)
    result = cursor.fetchone()
    if result is None and not ifExist(username):
         return "Invalid username"
    else:
        movies_string = result[0]
        movies_list = movies_string.split(',')
        movies_list.append(movie)
    movies_string = ','.join(movies_list)
    update_query = "UPDATE user SET Movies = %s WHERE username = %s"
    cursor.execute(update_query, (movies_string, username))
    cnx.commit()
    cursor.close()  
    cnx.close()


# returns the list of movies for corrosponds to the username
def Movie_list(username):
    cnx = get_db_connection()
    cursor = cnx.cursor()
    query = "SELECT Movies FROM user WHERE username = '"+username+"'"
    cursor.execute(query)
    result = cursor.fetchone()
    if result is None:
        movies_list = []
    else:
        movies_string = result[0]
        movies_list = movies_string.split(',')
        movies_list.remove(' ')
    cursor.close()
    cnx.close()
    return movies_list
# -------------------------------------------------------------------------------------------------------------------------
