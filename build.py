import mysql.connector
import os
mysql_host= os.environ.get('DB_HOST')
mysql_user= os.environ.get('DB_USER') 
mysql_password=  os.environ.get('DB_PASSWORD') 
mysql_port= os.environ.get('DB_PORT')
mysql_db= os.environ.get('DB_NAME') 
# Connect to MySQL server
mydb = mysql.connector.connect(
        host=mysql_host,
        user=mysql_user,
        password=mysql_password,
        port=mysql_port,
        database=mysql_db
)

# Create a cursor object
mycursor = mydb.cursor()

# Execute the CREATE TABLE statement
mycursor.execute("""
    CREATE TABLE IF NOT EXISTS user (
        UserID INT AUTO_INCREMENT PRIMARY KEY,
        Username VARCHAR(255) NOT NULL,
        Password VARCHAR(255) NOT NULL,
        Movies TEXT
    )
""")

# Commit the changes
mydb.commit()

# Close cursor and connection
mycursor.close()
mydb.close()
