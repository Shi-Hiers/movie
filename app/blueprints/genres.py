from flask import Blueprint, render_template, request, url_for, redirect, flash
from app.db_connect import get_db
#from app.functions import calculate_grade

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
        except ValueError:
            flash('Invalid input for genre', 'error')
        return redirect(url_for('genres.genre'))

    cursor.execute('SELECT * FROM genres')
    all_genres = cursor.fetchall()
    return render_template('genres.html', all_genres=all_genres)


@genres.route('/update_genre/<int:genre_id>', methods=['GET', 'POST'])
def update_genre(genre_id):
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        genre_name = request.form['genre_name']
        try:
            cursor.execute('UPDATE genres SET genre_name = %s WHERE genre_id = %s', (genre_name, genre_id))
            db.commit()
            flash('Genre updated successfully!', 'success')
        except ValueError:
            flash('Invalid input for genre', 'error')
        return redirect(url_for('genres.genre'))

    cursor.execute('SELECT * FROM genres WHERE genre_id = %s', (genre_id,))
    current_genre = cursor.fetchone()

    if current_genre is None:
        flash('Genre not found', 'error')
        return redirect(url_for('genres.genre'))

    return render_template('update_genre.html', current_genre=current_genre)

@genres.route('/delete_genre/<int:genre_id>', methods=['POST'])
def delete_genre(genre_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute('DELETE FROM genres WHERE genre_id = %s', (genre_id,))
    db.commit()
    return redirect(url_for('genres.genre'))