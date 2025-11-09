# -*- coding: utf-8 -*-
"""
    Flaskr
    ~~~~~~

    A microblog example application written as Flask tutorial with
    Flask and sqlite3.

    :copyright: (c) 2015 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, g, redirect, url_for, render_template, flash


# create our little application :)
app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='development key',
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/')
def show_entries():
    """Show the entries in a database. It shows title, text, and category"""

    # getting all entries for list
    db = get_db()
    cur = db.execute('select id, title, text, category from entries order by id desc')
    entries = cur.fetchall()

    # getting distinct categories for categories menu
    cur2 = db.execute('select distinct category from entries')
    rows = cur2.fetchall()
    categories = list()
    for row in rows:
        categories.append(row['category'])

    return render_template('show_entries.html', entries=entries, categories=categories)


@app.route('/add', methods=['POST'])
def add_entry():
    """Adds an entry to database. It adds an entry with a
    users title, text, and category"""

    # inserting the entry into the table then shows the
    # updated list with the newly added entry
    db = get_db()
    db.execute('insert into entries (title, text, category) values (?, ?, ?)',
               [request.form['title'], request.form['text'], request.form['category']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


@app.route('/show_selected', methods=['POST'])
def show_selected():
    """Shows entries of a specified category given by the user"""

    # getting the user desired category
    db  = get_db()
    selected_category = request.form['selected_category']

    # using that input to query a database for entries with
    # the specified category
    cur = db.execute('SELECT title, text, category FROM entries WHERE category = ?', [selected_category])
    entries = cur.fetchall()
    flash(f'Showing results for {selected_category}')

    # redirects home, showing all entries
    if selected_category == "all" or selected_category == "":
        return redirect(url_for('show_entries'))


    # had to copy and paste so the distinct categories
    # menu stays intact
    cur2 = db.execute('select distinct category from entries')
    rows = cur2.fetchall()
    categories = list()
    for row in rows:
        categories.append(row['category'])
    return render_template('show_entries.html', entries=entries, categories=categories, selected_category=selected_category)

@app.route('/delete_entry', methods=['POST'])
def delete_entry():
    """Deletes an entry from the table."""

    # getting the id of the desired post to delete
    db = get_db()
    selected_entry_id = request.form['deleted_post']

    # Deleting the entry from the database, which means
    # it won't show up when we redirect to the homepage
    cur = db.execute('DELETE from entries where id = ?', [selected_entry_id])
    db.commit()
    flash("Entry Deleted")
    return redirect(url_for('show_entries'))

@app.route('/edit_entry', methods=['POST'])
def edit_entry():
    """Sends users to a page to update a post."""

    # getting the post's old information and current id
    db = get_db()
    old_title = request.form['old_title']
    old_category = request.form['old_category']
    old_text = request.form['old_text']
    id = request.form['id']


    # redirecting to the edit entry page where the old information will remain
    # in the input fields
    return render_template('edit_entry.html', old_title=old_title, old_category=old_category, old_text=old_text, id = id )

@app.route('/update_edited_entry', methods=['POST'])
def update_edited_entry():
    """Allows users to update specific information on posts."""

    # updating the post's information in the database and commiting it
    db = get_db()
    db.execute('UPDATE entries SET title = ?, text = ?, category = ? WHERE id = ?',
               [request.form['updated_title'], request.form['updated_text'], request.form['updated_category'], request.form['id']] )
    db.commit()

    # informing the user that the entry was added after they ae redirected
    flash('New entry was successfully updated.')
    return redirect(url_for('show_entries'))