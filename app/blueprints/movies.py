from flask import Blueprint, render_template, request, url_for, redirect, flash
from app.db_connect import get_db
from app.functions import filter_movies_by_genre, filter_movies_by_title, filter_movies_by_year

movies = Blueprint('movies', __name__)

@movies.route('/movies', methods=['GET', 'POST'])
def movie():
    db = get_db()
    cursor = db.cursor()

    # Handle POST request to add a new movie
    if request.method == 'POST':
        movie_title = request.form['movie_title']
        release_year = request.form['release_year']
        genre_id = request.form['genre_id']

        # Insert the new movie into the database
        cursor.execute(
            'INSERT INTO movies (movie_title, release_year) VALUES (%s, %s)',
            (movie_title, release_year)
        )
        movie_id = cursor.lastrowid  # Get the newly inserted movie ID

        # Associate the movie with the selected genre
        cursor.execute(
            'INSERT INTO Movie_genres (movie_id, genre_id) VALUES (%s, %s)',
            (movie_id, genre_id)
        )
        db.commit()

        flash('New movie added successfully!', 'success')
        return redirect(url_for('movies.movie'))

    # Query to display all movies with concatenated genres
    cursor.execute("""
        SELECT m.movie_id, m.movie_title, m.release_year, GROUP_CONCAT(g.genre_name SEPARATOR ', ') AS genres
        FROM movies m
        LEFT JOIN Movie_genres mg ON m.movie_id = mg.movie_id
        LEFT JOIN genres g ON mg.genre_id = g.genre_id
        GROUP BY m.movie_id
    """)
    all_movies = cursor.fetchall()

    # Fetch all genres for the dropdown filter
    cursor.execute('SELECT * FROM genres')
    all_genres = cursor.fetchall()

    db.close()
    return render_template('movies.html', all_movies=all_movies, all_genres=all_genres)

@movies.route('/filter', methods=['GET'])
def filter_movies():
    # Get filter parameters from the query string
    genre_id = request.args.get('genre_id')
    movie_title = request.args.get('movie_title')
    release_year = request.args.get('release_year')

    db = get_db()
    cursor = db.cursor()

    # Determine which filter to apply
    if genre_id:
        movies = filter_movies_by_genre(genre_id)
    elif movie_title:
        movies = filter_movies_by_title(movie_title)
    elif release_year:
        movies = filter_movies_by_year(release_year)
    else:
        # If no filter is applied, fetch all movies with genres
        cursor.execute("""
            SELECT m.movie_id, m.movie_title, m.release_year, g.genre_name
            FROM movies m
            LEFT JOIN Movie_genres mg ON m.movie_id = mg.movie_id
            LEFT JOIN genres g ON mg.genre_id = g.genre_id
        """)
        movies = cursor.fetchall()

    # Fetch all genres for the dropdown
    cursor.execute('SELECT * FROM genres')
    all_genres = cursor.fetchall()
    db.close()

    return render_template('movies.html', all_movies=movies, all_genres=all_genres)


@movies.route('/update_movie/<int:movie_id>', methods=['GET', 'POST'])
def update_movie(movie_id):
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        # Get the updated movie details
        movie_title = request.form['movie_title']
        release_year = request.form['release_year']
        genre_ids = request.form.getlist('genre_ids')  # Multiple genres

        # Update the movie title and release year
        cursor.execute('UPDATE movies SET movie_title = %s, release_year = %s WHERE movie_id = %s',
                       (movie_title, release_year, movie_id))

        # Clear existing genres for the movie
        cursor.execute('DELETE FROM Movie_genres WHERE movie_id = %s', (movie_id,))

        # Add new genres
        for genre_id in genre_ids:
            cursor.execute('INSERT INTO Movie_genres (movie_id, genre_id) VALUES (%s, %s)', (movie_id, genre_id))

        db.commit()
        flash('Movie updated successfully!', 'success')
        return redirect(url_for('movies.movie'))

    # Fetch the movie's current details
    cursor.execute('SELECT movie_id, movie_title, release_year FROM movies WHERE movie_id = %s', (movie_id,))
    movie = cursor.fetchone()

    # Fetch all genres and the movie's current genres
    cursor.execute('SELECT * FROM genres')
    all_genres = cursor.fetchall()
    cursor.execute('SELECT genre_id FROM Movie_genres WHERE movie_id = %s', (movie_id,))
    movie_genres = [genre['genre_id'] for genre in cursor.fetchall()]

    db.close()
    return render_template('update_movie.html', movie=movie, all_genres=all_genres, movie_genres=movie_genres)


@movies.route('/delete_movie/<int:movie_id>', methods=['POST'])
def delete_movie(movie_id):
    db = get_db()
    cursor = db.cursor()

    try:
        # Delete all related entries in the Movie_genres table first
        cursor.execute('DELETE FROM Movie_genres WHERE movie_id = %s', (movie_id,))

        # Then delete the movie itself
        cursor.execute('DELETE FROM movies WHERE movie_id = %s', (movie_id,))

        db.commit()
        flash('Movie deleted successfully!', 'danger')

    except pymysql.MySQLError as e:
        db.rollback()
        flash(f"Error deleting movie: {e}", 'danger')

    finally:
        db.close()

    return redirect(url_for('movies.movie'))

@movies.route('/movie_search', methods=['GET', 'POST'])
def movie_search():
    db = get_db()
    cursor = db.cursor()

    # Initialize the base query
    query = "SELECT * FROM movies WHERE 1=1"
    params = []

    # Check if the form was submitted
    if request.method == 'POST':
        title_query = request.form.get('title_query', '').strip()
        year_query = request.form.get('year_query', '').strip()
        genre_query = request.form.get('genre_query', '').strip()

        # Filter by title if provided
        if title_query:
            query += " AND movie_title LIKE %s"
            params.append(f'%{title_query}%')

        # Filter by release year if provided
        if year_query:
            query += " AND release_year = %s"
            params.append(year_query)

        # Filter by genre if provided
        if genre_query:
            query += """
            AND movie_id IN (SELECT movie_id FROM Movie_genres WHERE genre_id = %s)
            """
            params.append(genre_query)

        # Execute the query with the parameters
        cursor.execute(query, params)
        search_results = cursor.fetchall()
    else:
        search_results = []

    # Fetch genres for the search form
    cursor.execute('SELECT * FROM genres')
    genres = cursor.fetchall()

    db.close()
    return render_template('movie_search.html', search_results=search_results, genres=genres)
