
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
movie_db = IMDb()
# given the name of the movie, gives the genres (category) of the movie
# @param name_of_the_movie --> takes the name of the movie
# @return Genres of the movie name given
def get_genres(name_of_the_movie: str):
    movies = movie_db.search_movie(name_of_the_movie)  # A list of all the movies for this name
    movie = movies[0]  # Get the first movie in the list
    movie_db.update(movie)
    genres = movie['genres']  # Get the Genres

    return genres[0]


# Given genres, generates a list of recommended movies
def get_recommended(genres: str, limit=10):
    top_movies = movie_db.get_top250_movies()
    recommended_movies = []
    for movie in top_movies:
        if genres.lower() in [genre.lower() for genre in movie.get('genres', [])]:
            recommended_movies.append(movie.get('title'))
        if len(recommended_movies) >= limit:
            break
    return recommended_movies

# Given a list of watched movies, returns a recommended list of movies
def get_recommended_list(list_of_movies):
    genre_appearances = {}
    for movie in list_of_movies:
        genres = get_genres(movie)
        for genre in genres:
            genre_appearances[genre] = genre_appearances.get(genre, 0) + 1
    if genre_appearances:
        max_genre = max(genre_appearances, key=genre_appearances.get)
        return get_recommended(max_genre)
    else:
        return []

# this function takes the movie title and returns its rating 
# @param movive title
# @return the rating in float  
def get_movie_rating(movie_title):
    
    # Search for the movie
    movie = movie_db.search_movie(movie_title)[0]
    movie_db.update(movie)
    
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
        #print(link)
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
        


@app.route('/success', methods=['GET', 'POST'])
def success():
    global counter
    counter = 1
    if len(Movie_list(UserName)) == 1:
        recommended_list = get_recommended('Drama')
    else:
        recommended_list = get_recommended_list(Movie_list(UserName))

    if counter < len(recommended_list):
        name = recommended_list[counter]
        genres = get_genres(name)
        youtube = find_trailer(name)
        rate = get_movie_rating(name)
    else:
        name = ""
        genres = ""
        youtube = ""
        rate = ""

    if request.method == 'POST':
        MovieInsert1 = request.form['MovieInsert']
        add_movie(UserName, MovieInsert1)
        recommended_list = get_recommended_list(Movie_list(UserName))
        if counter < len(recommended_list):
            name = recommended_list[counter]
            genres = get_genres(name)
            youtube = find_trailer(name)
            rate = get_movie_rating(name)
        else:
            name = ""
            genres = ""
            youtube = ""
            rate = ""
        return render_template('MovieRecommender.html', movie_list=Movie_list(UserName), youtube=youtube,
                               genres=genres, name=name, rate=rate)
    return render_template('MovieRecommender.html', movie_list=Movie_list(UserName), youtube=youtube, genres=genres,
                           name=name, rate=rate)



@app.route('/next', methods=['GET', 'POST'])
def nextMovie():
    global counter
    if request.method == 'POST':
        if len( Movie_list(UserName)) == 1:
            recommended_list = get_recommended('Drama')
            counter = counter + 1
            name = recommended_list[counter]
            genres = get_genres(name)
            youtube = find_trailer(name)
            rate = get_movie_rating(name)
        else:
            recommended_list = get_recommended_list(Movie_list(UserName))
            counter = counter + 1
            name = recommended_list[counter]
            genres = get_genres(name)
            youtube = find_trailer(name)
            rate = get_movie_rating(name)
        return render_template('MovieRecommender.html', movie_list = Movie_list(UserName), youtube = youtube, genres = genres, name = name, rate = rate )
    return render_template('MovieRecommender.html', movie_list = Movie_list(UserName), youtube = youtube, genres = genres, name = name, rate = rate )



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
    
