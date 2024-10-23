from app.db_connect import get_db


def get_all_genres():
    db = get_db()
    cursor = db.cursor()

    # Fetch genres
    query = "SELECT genre_id, genre_name FROM genres"
    cursor.execute(query)
    genres = cursor.fetchall()

    # Convert to a list of dictionaries for easier access
    results = [{'genre_id': g[0], 'genre_name': g[1]} for g in genres]
    return results


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
