from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
import config

app = Flask(__name__)
app.config['SECRET_KEY'] = 'enter secret key'
Bootstrap(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my-top-movies.db'
db = SQLAlchemy(app)


class Movie(db.Model):
    """
    A class to represent the Movie table in our My Top Movies DB
    (i.e. Database), which holds various information of my favourite
    movies.
    """

    # class attributes
    # ...

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.VARCHAR(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.VARCHAR(250), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.VARCHAR(250), nullable=True)
    img_url = db.Column(db.VARCHAR(250), nullable=False)


db.create_all()


@app.route("/")
def home():
    all_movies = db.session.query(Movie).all()
    print(all_movies)
    all_movie_ratings = db.session.query(Movie.rating).all()
    if all_movies:
        print(all_movie_ratings)
        less = []
        equal = []
        greater = []
        if len(all_movie_ratings) > 1:
            pivot = all_movie_ratings[0][0]
            for movie_rating_tuple in all_movie_ratings:
                if movie_rating_tuple[0] < pivot:
                    less.append(movie_rating_tuple[0])
                elif movie_rating_tuple[0] == pivot:
                    equal.append(movie_rating_tuple[0])
                elif movie_rating_tuple[0] > pivot:
                    greater.append(movie_rating_tuple[0])
            ordered_movie_ratings = greater + equal + less
            for movie_rating in ordered_movie_ratings:
                movie = db.session.query(Movie).filter(Movie.rating == movie_rating).first()
                movie.ranking = ordered_movie_ratings.index(movie_rating) + 1
            db.session.commit()
            all_movies = db.session.query(Movie).order_by(Movie.ranking).all()
            return render_template(template_name_or_list='./index.html', my_top_movies=all_movies)
        else:
            the_only_movie = db.session.query(Movie).first()
            the_only_movie.ranking = 1
            db.session.commit()
            return render_template(template_name_or_list='./index.html', my_top_movies=all_movies)
    else:
        return render_template("index.html", my_top_movies=[])


class EditForm(FlaskForm):
    """
    A class to represent the form used to update the top movie review details.
    """

    # class attributes
    # ...

    new_rating_data_required_validator = DataRequired()
    new_rating = StringField(u'Your Rating Out of 10 e.g. 7.5', validators=[new_rating_data_required_validator])
    new_review_data_required_validator = DataRequired()
    new_review = StringField(u'Your Review', validators=[new_review_data_required_validator])
    submit_btn = SubmitField('Done')


@app.route(rule='/edit', methods=['GET', 'POST', ])
def edit():
    form = EditForm()
    if form.validate_on_submit():
        movie_to_update_id = request.args.get('id')
        movie_to_update = Movie.query.get(movie_to_update_id)
        movie_to_update.rating = form.new_rating.data
        movie_to_update.review = form.new_review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template(template_name_or_list='./edit.html', edit_movie_form=form)


@app.route('/delete')
def delete():
    movie_to_delete_id = request.args.get('movie_id')
    movie_to_delete = Movie.query.get(movie_to_delete_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for(endpoint='home'))


class AddForm(FlaskForm):
    """
    A class to represent the form used to add a movie to the list of top movies.
    """

    # class attributes
    # ...

    new_top_movie_data_required_validator = DataRequired()
    new_movie_title = StringField(u'Movie Title', validators=[new_top_movie_data_required_validator])
    add_movie_btn = SubmitField('Add Movie')


TMDB_BASE_URL = 'enter base url'
TMDB_MOVIES_ENDPOINT = 'enter movies endpoint'


@app.route('/add', methods=['GET', 'POST', ])
def add():
    form = AddForm()
    if form.validate_on_submit():
        new_movie_title = form.new_movie_title.data
        url = TMDB_BASE_URL + TMDB_MOVIES_ENDPOINT
        params = {
            'api_key': config.TMDB_API_KEY,
            'query': new_movie_title
        }
        response = requests.get(url=url, params=params)
        response.raise_for_status()
        data = response.json()
        results = data['results']
        return render_template('./select.html', movie_search_results=results)
    return render_template(template_name_or_list='./add.html', add_movie_form=form)


@app.route('/select')
def select():
    the_movie_id = request.args.get('new_movie_to_add_id')
    url = TMDB_BASE_URL + f"type endpoint here"
    headers = {
        'Authorization': config.TMDB_BEARER_TOKEN,
        'Content-Type': 'application/json'
    }
    response = requests.get(url=url, headers=headers)
    response.raise_for_status()
    data = response.json()
    new_movie_title = data['title']
    new_movie_img_url = 'https://image.tmdb.org/t/p/w500' + data['poster_path']
    new_movie_year = data['release_date']
    new_movie_description = data['overview']
    new_movie_instance = Movie(
            title=new_movie_title,
            year=new_movie_year,
            description=new_movie_description,
            img_url=new_movie_img_url
    )
    db.session.add(new_movie_instance)
    db.session.commit()
    return redirect(url_for('edit', id=new_movie_instance.id))


if __name__ == '__main__':
    app.run(debug=True)
