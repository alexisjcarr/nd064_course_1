from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
import logging
import sqlite3
import sys
from werkzeug.exceptions import abort


root = logging.getLogger('app')
root.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

conn_counter = 0


def get_db_connection():
    """
    Function to get a database connection.
    This function connects to database with the name `database.db`
    """
    global conn_counter
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    conn_counter += 1
    return connection


def get_post(post_id):
    """
    Function to get a post using its ID
    """
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                              (post_id,)).fetchone()
    connection.close()
    return post


# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'


@app.route('/')
def index():
    """
    Define the main route of the web application
    """
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)


@app.route('/healthz')
def health_check():
    """
    write description
    """
    response = app.response_class(
        response=json.dumps(
            {
                "result": "OK — healthy"
            }
        ),
        status=200,
        mimetype='application/json'
    )

    return response


@app.route('/metrics')
def metrics():
    """
    write description
    """
    conn = get_db_connection()
    posts = conn.execute("select * from 'posts'").fetchall()
    conn.close()
    post_count = len(posts)
    response = app.response_class(
        response=json.dumps(
            {
                "status": "success",
                "code": 0,
                "data": {
                    "db_connection_count": conn_counter,
                    "post_count": post_count,
                }
            }
        ),
        status=200,
        mimetype='application/json'
    )

    return response


@app.route('/<int:post_id>')
def post(post_id):
    """
    Define how each individual article is rendered
    If the post ID is not found a 404 page is shown
    """
    post = get_post(post_id)
    post_title = post['title']
    if post is None:
        return render_template('404.html'), 404
    else:
        app.logger.info(f'Article "{post_title}" retrieved!')
        return render_template('post.html', post=post)


@app.route('/about')
def about():
    """
    Define the About Us page
    """
    return render_template('about.html')


@app.route('/create', methods=('GET', 'POST'))
def create():
    """
    Define the post creation functionality
    """
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                               (title, content))
            connection.commit()
            connection.close()

            return redirect(url_for('index'))

    return render_template('create.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='3111')
