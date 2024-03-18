
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
import tmdbsimple as tmdb
import requests


# -------------------------------------------------------------------------------------------------------------------------

app = Flask(__name__)

# ---------------------------------------------------------Movie Recommondation--------------------------------------------


# TMDb API key (replace 'YOUR_API_KEY' with your actual API key)
tmdb.API_KEY = 'a7a'
API_KEY = 'a7a'


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

    # Get top rated movies by specified genres
    discover_url = f"https://api.themoviedb.org/3/discover/movie?api_key={API_KEY}&sort_by=vote_average.desc&with_genres={genre_ids}"
    response = requests.get(discover_url)
    data = response.json()

    # Extract top 10 movie titles
    top_10_movies = [movie['title'] for movie in data['results'][:10]]

    return top_10_movies


# Helper function to get TMDb genre IDs by genre names
def get_genre_ids(genres):
    genre_list_url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={API_KEY}"
    response = requests.get(genre_list_url)
    data = response.json()
    genre_ids = []

    for genre in genres:
        for item in data['genres']:
            if item['name'] == genre:
                genre_ids.append(item['id'])
                break

    return genre_ids



# checks for the most watched genres
# @param list_of_movies: list of watched movies by name
# @return recommended list of movies
def get_recommended_list(list_of_movies):
    genre_list = []
    genres = ['Comedy', 'Romance', 'Drama', 'Animation', 'Science Fiction', 'Action',
              'Mystery', 'Adventure', 'Horror', 'Crime',
              'Fantasy', 'Science Fiction']
    number_of_appearances = [0] * len(genres)
    maxAppearance = 0
    maxIndex = 0

    for movie_title in list_of_movies:
        genre = get_genres(movie_title)
        if genre:
            genre_list.append(genre)

    # updating number of appearance of each genre
    for genre in genre_list:
        for index, genre_name in enumerate(genres):
            if genre == genre_name:
                number_of_appearances[index] += 1
                if number_of_appearances[index] > maxAppearance:
                    maxAppearance = number_of_appearances[index]
                    maxIndex = index

    return get_recommended(genres[maxIndex])


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

# Example usage:
movie_name = "Inception"
movie_genres = get_genres(movie_name)
if movie_genres:
    recommended_movies = get_recommended(movie_genres)
    print(f"Top 10 recommended movies for {movie_name} genres:", recommended_movies)
else:
    print("Movie not found.")


# ---------------------------------------------------------Youtube Api----------------------------------------------------
# Find trailer using youtube API
def find_trailer(name):
    api_key = "A7A"

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

## regester the username and password to the database
def add(username,password):
    mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Androwmaged3030",
    database="MovieRecommender"
    )
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
    mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Androwmaged3030",
    database="MovieRecommender"
    )

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
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Androwmaged3030",
        database="MovieRecommender"
        )
    try:
        with mydb.cursor() as cursor:
            # Execute the SELECT statement to retrieve the stored password for the given username
            sql = "SELECT Password FROM user WHERE Username = %s"
            cursor.execute(sql, (username,))
            result = cursor.fetchone()
            # Compare the stored password to the input password
            if result['Password'] == password:
                print("Password match.")
            else:
                print("Password does not match.")
    finally:
        mydb.close()

        return result


# add function that add a movie to the list of movies for every user
def add_movie(username, movie):
    cnx = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Androwmaged3030",
        database="MovieRecommender"
        )
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
    cnx = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Androwmaged3030",
        database="MovieRecommender"
        )
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
if __name__ == '__main__':
    app.run(debug=True)
    