from flask import Blueprint, render_template, request, url_for, redirect, flash
from app.db_connect import get_db
from app.functions import filter_movies_by_genre, filter_movies_by_title, filter_movies_by_year  # Import functions here

movies = Blueprint('movies', __name__)

@movies.route('/movies', methods=['GET', 'POST'])
def movie():
    db = get_db()
    cursor = db.cursor()

    # Handle POST request to add a new movie
    if request.method == 'POST':
        movie_title = request.form['movie_title']
        release_year = request.form['release_year']

        # Insert the new movie into the database
        cursor.execute(
            'INSERT INTO movies (movie_title, release_year) VALUES (%s, %s)',
            (movie_title, release_year)
        )
        db.commit()

        flash('New movie added successfully!', 'success')
        return redirect(url_for('movies.movie'))

    # Handle GET request to display all movies
    cursor.execute('SELECT * FROM movies')
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

    # Determine which filter to apply
    if genre_id:
        # Use the function to filter by genre
        movies = filter_movies_by_genre(genre_id)
    elif movie_title:
        # Use the function to filter by title
        movies = filter_movies_by_title(movie_title)
    elif release_year:
        # Use the function to filter by release year
        movies = filter_movies_by_year(release_year)
    else:
        db = get_db()
        cursor = db.cursor()
        # If no filter is applied, fetch all movies
        cursor.execute('SELECT * FROM movies')
        movies = cursor.fetchall()
        db.close()

    # Fetch all genres for the dropdown
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM genres')
    all_genres = cursor.fetchall()
    db.close()

    # Render the template with the filtered movies and genre list
    return render_template('movies.html', all_movies=movies, all_genres=all_genres)

@movies.route('/update_movie/<int:movie_id>', methods=['GET', 'POST'])
def update_movie(movie_id):
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        movie_title = request.form['movie_title']
        release_year = request.form['release_year']

        cursor.execute('UPDATE movies SET movie_title = %s, release_year = %s WHERE movie_id = %s',
                       (movie_title, release_year, movie_id))
        db.commit()

        flash('Movie updated successfully!', 'success')
        return redirect(url_for('movies.movie'))

    cursor.execute('SELECT movie_id, movie_title, release_year FROM movies WHERE movie_id = %s', (movie_id,))
    movie = cursor.fetchone()

    if movie is None:
        flash('Movie not found!', 'danger')
        return redirect(url_for('movies.movie'))

    db.close()
    return render_template('update_movie.html', movie=movie)

@movies.route('/delete_movie/<int:movie_id>', methods=['POST'])
def delete_movie(movie_id):
    db = get_db()
    cursor = db.cursor()

    # Delete the movie
    cursor.execute('DELETE FROM movies WHERE movie_id = %s', (movie_id,))
    db.commit()

    flash('Movie deleted successfully!', 'danger')
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
