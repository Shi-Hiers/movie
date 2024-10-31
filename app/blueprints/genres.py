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

# Updated update_genre route without movie_id
@genres.route('/update_genre/<int:genre_id>', methods=['GET', 'POST'])
def update_genre(genre_id):
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        new_genre_name = request.form.get('genre_name')

        if not new_genre_name:
            flash('Genre name is required!', 'danger')
            return redirect(url_for('genres.update_genre', genre_id=genre_id))

        # Find genre by ID and update
        cursor.execute('UPDATE genres SET genre_name = %s WHERE genre_id = %s',
                       (new_genre_name, genre_id))
        db.commit()

        flash('Genre updated successfully!', 'success')
        return redirect(url_for('genres.genre'))

    # Fetch current genre information
    cursor.execute('SELECT genre_id, genre_name FROM genres WHERE genre_id = %s', (genre_id,))
    current_genre_dict = cursor.fetchone()

    if current_genre_dict is None:
        flash(f'Genre with ID {genre_id} not found!', 'danger')
        return redirect(url_for('genres.genre'))

    current_genre = {'genre_id': current_genre_dict['genre_id'], 'genre_name': current_genre_dict['genre_name']}
    return render_template('update_genre.html', current_genre=current_genre)

@genres.route('/delete_genre/<int:genre_id>', methods=['POST'])
def delete_genre(genre_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute('DELETE FROM genres WHERE genre_id = %s', (genre_id,))
    db.commit()

    flash('Genre deleted successfully!', 'danger')
    return redirect(url_for('genres.genre'))

@genres.route('/assign_genre', methods=['GET', 'POST'])
def assign_genre_to_movie():
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        movie_id = request.form['movie_id']
        genre_name = request.form['genre_name']

        cursor.execute('SELECT genre_id FROM genres WHERE genre_name = %s', (genre_name,))
        genre = cursor.fetchone()

        if genre is None:
            cursor.execute('INSERT INTO genres (genre_name) VALUES (%s)', (genre_name,))
            db.commit()
            new_genre_id = cursor.lastrowid
        else:
            new_genre_id = genre['genre_id']

        cursor.execute('INSERT INTO Movie_genres (movie_id, genre_id) VALUES (%s, %s)',
                       (movie_id, new_genre_id))
        db.commit()

        flash('Genre assigned to movie successfully!', 'success')
        return redirect(url_for('genres.assign_genre_to_movie'))

    # Fetch all movies
    cursor.execute('SELECT * FROM movies')
    all_movies = cursor.fetchall()

    # Fetch movies with genres
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
            'release_year': entry['release_year'],
            'genre_id': entry['genre_id'],
            'genre_name': entry['genre_name']
        }
        for entry in movies_with_genres
    ]

    return render_template('genres.html', all_movies=all_movies, movies_with_genres=movies_with_genres)
