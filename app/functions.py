from app.db_connect import get_db

# Function to filter movies by genre
def filter_movies_by_genre(genre_id):
    db = get_db()
    cursor = db.cursor()

    query = """
    SELECT m.movie_id, m.movie_title, m.release_year
    FROM movies m
    JOIN Movie_genres mg ON m.movie_id = mg.movie_id
    WHERE mg.genre_id = %s
    """
    cursor.execute(query, (genre_id,))
    movies = cursor.fetchall()

    return movies

# Function to filter movies by title
def filter_movies_by_title(movie_title):
    db = get_db()
    cursor = db.cursor()

    query = """
    SELECT movie_id, movie_title, release_year
    FROM movies
    WHERE movie_title LIKE %s
    """
    cursor.execute(query, ('%' + movie_title + '%',))
    movies = cursor.fetchall()

    return movies

# Function to filter movies by release year
def filter_movies_by_year(release_year):
    db = get_db()
    cursor = db.cursor()

    query = """
    SELECT movie_id, movie_title, release_year
    FROM movies
    WHERE release_year = %s
    """
    cursor.execute(query, (release_year,))
    movies = cursor.fetchall()

    return movies
