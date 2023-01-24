
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
    top_movies = movie_db.get_top50_movies_by_genres(genres)  # best 50 movies according to the genres
    top_10_movies = []
    for j in range(10):
        top_10_movies.append(top_movies[j]['title'])  # best 10 movies according to the genres

    return top_10_movies


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

# -------------------------------------------------------------------------------------------------------------------------





# ---------------------------------------------------------Youtube Api----------------------------------------------------
# Find trailer using youtube API
def find_trailer(name):
    api_key = "AIzaSyCHS5GOUVKJuxxkVOZSKxr0EKfNJmfIDKc"

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

# ---------------------------------------------------------Get Information----------------------------------------------------

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
                return redirect('/success')
        else:
            return render_template('LoginScreen.html')
    return render_template('LoginScreen.html')

@app.route('/success')
def success():
    return render_template('index.html')



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
    sql = "INSERT INTO user (Username, Password) VALUES (%s, %s)"
    val = (username, password)
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

# -------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)