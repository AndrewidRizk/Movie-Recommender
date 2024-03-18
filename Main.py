
# ---------------------------------------------------------import Files---------------------------------------------------
# importing required APIs and pachages
from string import punctuation
from flask import Flask, render_template, request, url_for, redirect, session
import requests
from imdb import IMDb
import imdb
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import mysql.connector



# -------------------------------------------------------------------------------------------------------------------------

app = Flask(__name__)

# ---------------------------------------------------------Movie Recommondation--------------------------------------------
# given the name of the movie, gives the genres (category) of the movie
# @param name_of_the_movie --> takes the name of the movie
# @return Genres of the movie name given
def get_genres(name_of_the_movie: str):
    movie_db = IMDb()  # Data Base of IMDb
    movies = movie_db.search_movie(name_of_the_movie)  # A list of all the movies for this name
    movie = movies[0]  # Get the first movie in the list
    movie_db.update(movie)
    genres = movie['genres']  # Get the Genres

    return genres[0]


# given the genres, generate a list of recommendations
# @param genres --> takes the genres
# @return A list of top 10 recommended movies
def get_recommended(genres: str):
    movie_db = imdb.IMDb()
    top_movies = movie_db.get_top250_movies()  # Get top 250 movies
    recommended_movies = []

    # Iterate through the top movies and filter by genres
    for movie in top_movies:
        movie_db.update(movie)
        movie_genres = movie.get('genres', [])
        if genres.lower() in [genre.lower() for genre in movie_genres]:
            recommended_movies.append(movie['title'])
            if len(recommended_movies) == 10:
                break

    return recommended_movies


# checks for the most watched genres
# @param list_of_movies: list of watched movies by name
# @return recommended list of movies
def get_recommended_list(list_of_movies):
    genre_list = []
    genres = ['Comedy', 'Romance', 'Drama', 'Animation', 'SCI-FI', 'Action',
              'Mystery', 'Adventure', 'Horror', 'Crime',
              'Fantasy', 'SuperHero']
    number_of_appearances = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    maxAppearance = 0
    maxIndex = 0

    for z in range(len(list_of_movies)):
        genre_list.append(get_genres(list_of_movies[z]))

    # updating number of appearance of each genre
    for y in genre_list:
        for x in range(12):
            if y == genres[x]:
                number_of_appearances[x] = number_of_appearances[x] + 1
                if number_of_appearances[x] > maxAppearance:
                    maxAppearance = number_of_appearances[x]
                    maxIndex = x

    return get_recommended(genres[maxIndex])

# this function takes the movie title and returns its rating 
# @param movive title
# @return the rating in float  
def get_movie_rating(movie_title):
    # Initialize the IMDb class
    ia = IMDb()
    
    # Search for the movie
    movie = ia.search_movie(movie_title)[0]
    ia.update(movie)
    
    # Get the rating of the movie
    rating = movie.get('rating', 'N/A')
    return rating
# -------------------------------------------------------------------------------------------------------------------------



# ---------------------------------------------------------Youtube Api----------------------------------------------------
# Find trailer using youtube API
def find_trailer(name):
    api_key = "Enter your API key"

    movie_name =  name

    search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={movie_name}+trailer&type=video&key={api_key}"

    response = requests.get(search_url)

    data = response.json()

    if data["items"]:
        video_id = data["items"][0]["id"]["videoId"]
        link = "https://www.youtube.com/embed/"+video_id
    else:
        print("No video found.")

    return link

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
            if password == ConfirmPassword:
                add(username,password)
                return render_template('LoginScreen.html')
            else:
                return render_template('SignUpScreen.html')
        else:
            return render_template('SignUpScreen.html')
    else:
            return render_template('SignUpScreen.html')
        


counter = 0  # Initialize the counter outside of any function

@app.route('/success', methods=['GET', 'POST'])
def success():
    global counter
    counter = 0  # Reset counter to 0 upon entering the success route
    if len( Movie_list(UserName)) == 1:
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
        if len(Movie_list(UserName)) == 1:
            recommended_list = get_recommended('Drama')
            counter += 1  # Increment counter
            if counter < len(recommended_list):  # Check if counter is within bounds
                name = recommended_list[counter]
                # Rest of the code for getting genres, trailer, and rating...
        else:
            recommended_list = get_recommended_list(Movie_list(UserName))
            counter += 1  # Increment counter
            if counter < len(recommended_list):  # Check if counter is within bounds
                name = recommended_list[counter]
                # Rest of the code for getting genres, trailer, and rating...
        return render_template('MovieRecommender.html', movie_list=Movie_list(UserName), youtube=youtube, genres=genres, name=name, rate=rate)
    return render_template('MovieRecommender.html', movie_list=Movie_list(UserName), youtube=youtube, genres=genres, name=name, rate=rate)



# ------------------------------------------------MYSQL-------------------------------------------------------

import mysql.connector

# Connect to MySQL server
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Androwmaged3030"
)

# Create database if not exists
mycursor = mydb.cursor()
mycursor.execute("CREATE DATABASE IF NOT EXISTS MovieRecommender")
mydb.commit()

# Use the database
mycursor.execute("USE MovieRecommender")
mydb.commit()

# Create 'user' table if not exists
mycursor.execute("""
    CREATE TABLE IF NOT EXISTS user (
        UserID INT AUTO_INCREMENT PRIMARY KEY,
        Username VARCHAR(255) NOT NULL,
        Password VARCHAR(255) NOT NULL,
        Movies TEXT
    )
""")
mydb.commit()

# Close cursor and connection
mycursor.close()
mydb.close()

# Define functions
def add(username, password):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Androwmaged3030",
        database="MovieRecommender"
    )
    mycursor = mydb.cursor()
    sql = "INSERT INTO user (Username, Password, Movies) VALUES (%s, %s, %s)"
    val = (username, password, " ")
    mycursor.execute(sql, val)
    mydb.commit()
    mycursor.close()
    mydb.close()

def ifExist(username):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Androwmaged3030",
        database="MovieRecommender"
    )
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM user WHERE Username = %s", (username,))
    result = mycursor.fetchall()
    mycursor.close()
    mydb.close()
    return result

def if_Password_is_right(username, password):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Androwmaged3030",
        database="MovieRecommender"
    )
    try:
        with mydb.cursor() as cursor:
            sql = "SELECT Password FROM user WHERE Username = %s"
            cursor.execute(sql, (username,))
            result = cursor.fetchone()
            if result and result[0] == password:
                print("Password match.")
            else:
                print("Password does not match.")
    finally:
        mydb.close()
        return result

def add_movie(username, movie):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Androwmaged3030",
        database="MovieRecommender"
    )
    cursor = mydb.cursor()
    query = "SELECT Movies FROM user WHERE username = %s"
    cursor.execute(query, (username,))
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
        mydb.commit()
    cursor.close()
    mydb.close()

def Movie_list(username):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Androwmaged3030",
        database="MovieRecommender"
    )
    cursor = mydb.cursor()
    query = "SELECT Movies FROM user WHERE username = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    if result is None:
        movies_list = []
    else:
        movies_string = result[0]
        movies_list = movies_string.split(',')
        movies_list.remove(' ')
    cursor.close()
    mydb.close()
    return movies_list


# -------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
    
