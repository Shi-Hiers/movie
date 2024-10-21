from flask import render_template, request, url_for, redirect, flash
from . import app
from app.db_connect import get_db
from app.functions import calculate_grade


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')

