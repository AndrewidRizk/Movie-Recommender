# Movie-Recommender
A movie recommender a website that uses IMDB and YouTube APIs, And stores the users Userename, Passowrd, and movie list in a SQL database. then uses his movie list to generate a recommended movie list according to his most watched genres.

![image](https://user-images.githubusercontent.com/97995173/215014937-91e47e81-62c0-438d-8221-45119b5b36ff.png)


# packages to install ⬇
- pip install flask
- pip install imdbpy
- pip install --upgrade google-api-python-client
- pip install mysql-connector-python

# About the website and the Data Base 
When you chlick on login, it takes you to the login screen, And ask you to login using username and password, and we dont have any users in the data base

![image](https://user-images.githubusercontent.com/97995173/215023079-8ad01ab7-5db1-46f7-91f4-725a2f13494b.png)

so if you tried to login you will be asked to write username and password again we will need to sign up

![image](https://user-images.githubusercontent.com/97995173/215023274-8460c449-cef7-43e5-9e8e-7ae9cbab0c3a.png)

Lets sign up with the username Andrewid and password Andrewid 

![image](https://user-images.githubusercontent.com/97995173/215023457-8785fa3f-43e6-4b85-89b8-1c9c76728dd9.png)

And try to login again, As you can see A username and passowrd are added to the database 

![image](https://user-images.githubusercontent.com/97995173/215023786-b7abfaa9-7793-4e43-9a1d-2d6922b1f656.png)

And when you click login now it will take you to the home page 

![image](https://user-images.githubusercontent.com/97995173/215023841-702dded9-3fe6-4d43-bc24-ed39d4cd5852.png)

Before inserting anymovies the website will recommend some of the best movies up to date, Showing the name of the movie, rating, and the genres

![image](https://user-images.githubusercontent.com/97995173/215024197-545b04cd-8498-4c7b-9dac-2f5f0076821e.png)

When you add a movie in your movie list the recommender will recommend movies depends on the genres of the movies that you added in your movie list 

![image](https://user-images.githubusercontent.com/97995173/215024766-ce13ee05-3699-4c00-b990-0ac8d0ac97b4.png)

And the more movie you add the best the recommended movies 



