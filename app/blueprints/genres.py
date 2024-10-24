from flask import Blueprint, render_template, request, url_for, redirect, flash
from app.db_connect import get_db

genres = Blueprint('genres', __name__)

@genres.route('/genre', methods=['GET', 'POST'])
def genre():
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        genre_name = request.form['genre_name']
        try:
            cursor.execute('INSERT INTO genres (genre_name) VALUES (%s)', (genre_name,))
            db.commit()
            flash('Genre added successfully!', 'success')
        except Exception as e:
            flash(f'Error adding genre: {e}', 'danger')
        return redirect(url_for('genres.genre'))

    cursor.execute('SELECT * FROM genres')
    all_genres = cursor.fetchall()
    all_genres = [{'genre_id': genre['genre_id'], 'genre_name': genre['genre_name']} for genre in all_genres]
    return render_template('genres.html', all_genres=all_genres)

@genres.route('/update_genre/<int:movie_id>/<int:genre_id>', methods=['GET', 'POST'])
def update_genre(movie_id, genre_id):
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        # Use .get() to avoid KeyError
        new_genre_name = request.form.get('genre_name')

        if not new_genre_name:
            flash('Genre name is required!', 'danger')
            return redirect(url_for('genres.update_genre', movie_id=movie_id, genre_id=genre_id))

        # Proceed with the logic
        # Find genre by name
        cursor.execute('SELECT genre_id FROM genres WHERE genre_name = %s', (new_genre_name,))
        genre = cursor.fetchone()

        if genre is None:
            # Insert new genre if it does not exist
            cursor.execute('INSERT INTO genres (genre_name) VALUES (%s)', (new_genre_name,))
            db.commit()
            new_genre_id = cursor.lastrowid
        else:
            new_genre_id = genre['genre_id']

        # Update the movie genre relationship
        cursor.execute('UPDATE Movie_genres SET genre_id = %s WHERE movie_id = %s AND genre_id = %s',
                       (new_genre_id, movie_id, genre_id))
        db.commit()

        flash('Genre updated successfully!', 'success')
        return redirect(url_for('genres.assign_genre_to_movie'))

    # Fetch movie information
    cursor.execute('SELECT movie_title, release_year FROM movies WHERE movie_id = %s', (movie_id,))
    movie_dict = cursor.fetchone()

    # Check if the movie was found
    if movie_dict is None:
        flash(f'Movie with ID {movie_id} not found!', 'danger')
        return redirect(url_for('genres.assign_genre_to_movie'))

    # Use the dictionary directly
    movie = {'movie_id': movie_id, 'movie_title': movie_dict['movie_title'], 'release_year': movie_dict['release_year']}

    # Fetch current genre information
    cursor.execute('SELECT genre_id, genre_name FROM genres WHERE genre_id = %s', (genre_id,))
    current_genre_dict = cursor.fetchone()

    # Check if the current genre was found
    if current_genre_dict is None:
        flash(f'Genre with ID {genre_id} not found!', 'danger')
        return redirect(url_for('genres.assign_genre_to_movie'))

    current_genre = {'genre_id': current_genre_dict['genre_id'], 'genre_name': current_genre_dict['genre_name']}

    return render_template('update_genre.html', movie=movie, current_genre=current_genre)

@genres.route('/delete_genre/<int:movie_id>/<int:genre_id>', methods=['POST'])
def delete_genre(movie_id, genre_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute('DELETE FROM Movie_genres WHERE movie_id = %s AND genre_id = %s', (movie_id, genre_id))
    db.commit()

    flash('Genre removed from movie successfully!', 'danger')
    return redirect(url_for('genres.assign_genre_to_movie'))

@genres.route('/assign_genre', methods=['GET', 'POST'])
def assign_genre_to_movie():
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        movie_id = request.form['movie_id']
        genre_name = request.form['genre_name']

        # Check if the genre already exists
        cursor.execute('SELECT genre_id FROM genres WHERE genre_name = %s', (genre_name,))
        genre = cursor.fetchone()

        if genre is None:
            # If the genre does not exist, insert it
            cursor.execute('INSERT INTO genres (genre_name) VALUES (%s)', (genre_name,))
            db.commit()
            new_genre_id = cursor.lastrowid
        else:
            new_genre_id = genre['genre_id']

        # Now assign the genre to the movie in the Movie_genres table
        cursor.execute('INSERT INTO Movie_genres (movie_id, genre_id) VALUES (%s, %s)',
                       (movie_id, new_genre_id))
        db.commit()

        flash('Genre assigned to movie successfully!', 'success')
        return redirect(url_for('genres.assign_genre_to_movie'))

    # Fetch all movies
    cursor.execute('SELECT * FROM movies')
    all_movies = cursor.fetchall()

    # Fetch movies with genres, including release_year
    cursor.execute("""
        SELECT m.movie_id, m.movie_title, m.release_year, g.genre_id, g.genre_name
        FROM movies m
        LEFT JOIN Movie_genres mg ON m.movie_id = mg.movie_id
        LEFT JOIN genres g ON mg.genre_id = g.genre_id
    """)
    movies_with_genres = cursor.fetchall()

    movies_with_genres = [
        {
            'movie_id': entry['movie_id'],
            'movie_title': entry['movie_title'],
            'release_year': entry['release_year'],  # Add release_year here
            'genre_id': entry['genre_id'],
            'genre_name': entry['genre_name']
        }
        for entry in movies_with_genres
    ]

    return render_template('genres.html', all_movies=all_movies, movies_with_genres=movies_with_genres)

