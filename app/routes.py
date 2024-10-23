from flask import render_template, request, url_for, redirect, flash
from . import app
from app.db_connect import get_db


@app.route('/')
def movies():
    return render_template('movies.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/add_movie', methods=['GET', 'POST'])
def add_movie():
    if request.method == 'POST':
        # Handle form submission logic here
        movie_title = request.form['movie_title']
        release_year = request.form['release_year']

        # Add the movie to the database
        db = get_db()
        cursor = db.cursor()
        cursor.execute('INSERT INTO movies (movie_title, release_year) VALUES (%s, %s)', (movie_title, release_year))
        db.commit()

        flash('Movie added successfully!', 'success')
        return redirect(url_for('movies'))  # Redirect to the movies page after adding the movie

    return render_template('add_movie.html')


@app.route('/all_movies', methods=['GET'])
def all_movies():
    db = get_db()
    cursor = db.cursor()

    # Query to fetch all movies in the database
    cursor.execute('SELECT * FROM movies')
    all_movies = cursor.fetchall()

    return render_template('all_movies.html', all_movies=all_movies)