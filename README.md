# Overview
A website that uses TMDB and YouTube APIs, And stores the users Userename, Passowrd, and movie list in a SQL database. then uses his movie list to generate a recommended movie list according to his most watched genres.

![image](https://github.com/AndrewidRizk/Movie-Recommender/assets/97995173/36529477-c46d-4c0a-95e5-a337da17cad9)



# packages to install ⬇
- pip install flask
- pip install --upgrade google-api-python-client
- pip install mysql-connector-python

# About the website and the Data Base 
When you chlick on login, it takes you to the login screen, And ask you to login using username and password. Here is an interface to the USER table in my database.

![image](https://github.com/AndrewidRizk/Movie-Recommender/assets/97995173/03597bdf-a61a-48e8-9a6c-4016940820af)

If you don't have an account. You will need to sign up

![image](https://github.com/AndrewidRizk/Movie-Recommender/assets/97995173/30522d30-2b1d-40e2-b9f7-c499c76787f6)

Lets sign up with the username Andrewid and password Andrewid 

![image](https://github.com/AndrewidRizk/Movie-Recommender/assets/97995173/5af07a93-47f1-43cc-9386-f917e0443d7c)

As you can see Andrewid was added as a username and passowrd in the database 

![image](https://github.com/AndrewidRizk/Movie-Recommender/assets/97995173/5b16c708-bb8e-47fe-9e5e-c7929f4bc137)

And when you click login now it will take you to the home page 

![image](https://github.com/AndrewidRizk/Movie-Recommender/assets/97995173/4b2b1c62-e4f6-4f5d-9ed1-f5c95246ca75)

Before inserting anymovies the website will recommend some of the Top hits movies up to date, Showing the name of the movie, rating, and the genres

![image](https://github.com/AndrewidRizk/Movie-Recommender/assets/97995173/3bd0e6aa-80db-4b9c-af96-8fc8454d6ae1)

When you add a movie in your movie list the recommender will recommend movies depends on the genres of the movies that you added in your movie list 

![image](https://github.com/AndrewidRizk/Movie-Recommender/assets/97995173/b29a7f4a-06ea-483a-8e40-6d18a941290b)

And the more movie you add the better the recommended movies 



