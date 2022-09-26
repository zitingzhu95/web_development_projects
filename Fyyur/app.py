# ----------------------------------------------------------------------------#
# Imports.
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
  Flask,
  jsonify,
  render_template,
  request,
  Response,
  flash,
  redirect,
  url_for
)
from flask_moment import Moment
from flask_sqlalchemy import Model, SQLAlchemy
from sqlalchemy import func, inspect, or_
from datetime import datetime
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm, Form
from forms import *
from flask_migrate import Migrate
from model import *




# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)




# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime
datetimenow = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ----------------------------------------------------------------------------#
# Costomized Functions.
# ----------------------------------------------------------------------------#

def query_to_list(sql_query):
    if sql_query is None:
        return []
    rows = []
    for row in sql_query:
        data_list = []
        for data in row:
            data_list.append(data)
        rows.append(data_list)
    return rows


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    artists = db.session.query(Artist).\
        order_by(Artist.id.desc()).limit(10)
    venues = db.session.query(Venue).\
        order_by(Venue.id.desc()).limit(10)
    return render_template(
      'pages/home.html',
      artists=artists,
      venues=venues
      )


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    areas = db.session.\
      query(
        Venue.city.label("city"),
        Venue.state.label("state")
        ).\
      group_by(Venue.city, Venue.state).all()
    data = []
    for area in areas:
        data.append({"city": area.city, "state": area.state})

    for place in data:
        venues = db.session.\
          query(
            Venue.id.label("id"),
            Venue.name.label("name")
            ).\
          filter(Venue.city == place['city'])
        venues = query_to_list(venues)
        for venue in venues:
            num_upcoming_shows = db.session.\
              query(func.count(Show.start_time)).\
              filter(Show.venue_id == venue[0]).\
              filter(datetimenow < Show.start_time).all()
            venue.append(num_upcoming_shows[0][0])
        place['venues'] = [
          {"id": venue[0], "name": venue[1], "num_upcoming_shows": venue[2]}
          for venue in venues
          ]
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    venues = db.session.query(Venue).\
      filter(
        or_(
          func.lower(Venue.city).
          ilike(f'%' + request.form.get('search_term', '') + '%'),
          func.lower(Venue.state).
          ilike(f'%' + request.form.get('search_term', '') + '%'),
          func.lower(Venue.name).
          ilike(f'%' + request.form.get('search_term', '') + '%')
          )
        ).order_by(Venue.id).all()
    response = {
        "count": len(venues),
        "data": [
            {
              "id": venue.id,
              "name": venue.name,
              "num_upcoming_shows":
              len(
                db.session.
                query(func.count(Show.start_time)).
                filter(Show.venue_id == venue.id).
                filter(datetimenow < Show.start_time).all()
              )
            } for venue in venues]
    }
    return render_template(
        'pages/search_venues.html',
        results=response,
        search_term=request.form.get('search_term', '')
        )


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    data = db.session.query(Venue).get(venue_id)
    data.past_shows = db.session.\
      query( 
        Artist.id.label("artist_id"),
        Artist.name.label("artist_name"),
        Artist.image_link.label("artist_image_link"),
        Show.start_time.label("start_time")
        ).\
        join(Show).\
            filter(
              Show.venue_id == venue_id,
              Show.artist_id == Artist.id,
              Show.start_time < datetimenow
            ).all()

    data.upcoming_shows = db.session.\
      query( 
        Artist.id.label("artist_id"),
        Artist.name.label("artist_name"),
        Artist.image_link.label("artist_image_link"),
        Show.start_time.label("start_time")
        ).\
        join(Show).\
          filter(
            Show.venue_id == venue_id,
            Show.artist_id == Artist.id,
            Show.start_time > datetimenow
            ).all()
    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm()
    if form.validate_on_submit():
        try:
            newVenue = Venue(
                name=request.form['name'],
                city=request.form['city'],
                state=request.form['state'],
                address=request.form['address'],
                phone=request.form['phone'],
                genres=request.form.getlist('genres'),
                facebook_link=request.form['facebook_link'],
                image_link=request.form['image_link'],
                seeking_talent='seeking_talent' in request.form,
                seeking_description=request.form['seeking_description']
            )
            db.session.add(newVenue)
            db.session.commit()
            flash(
              'Venue ' +
              request.form['name'] +
              ' was successfully listed!', 'massage'
              )
        except BaseException:
            flash(
              'An error occurred. Venue ' +
              request.form['name'] +
              ' could not be listed.'
            )
        finally:
            db.session.close()
        return redirect(url_for('index'))
    else:
        print(form.errors)
        flash(
          'An error occurred. \
          Venue could not be validated. \
          Please use the right format' 
          )
        flash( 
          form.errors
        )
        return render_template('forms/new_venue.html', form=form)


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    artists = db.session.query(Artist).all()
    data = []
    for artist in artists:
        data.append({"id": artist.id, "name": artist.name})

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    artists = db.session.query(Artist).\
        filter(
            or_(
                func.lower(Artist.city).
                ilike(
                  f'%' + request.form.get('search_term', '') + '%'
                  ),
                func.lower(Artist.state).
                ilike(
                  f'%' + request.form.get('search_term', '') + '%'
                  ),
                func.lower(Artist.name).
                ilike(
                  f'%' + request.form.get('search_term', '') + '%'
                  )
            )
        ).order_by(Artist.id).all()
    response = {
      "count": len(artists),
      "data": [
          {
              "id": artist.id,
              "name": artist.name,
              "num_upcoming_shows":
                  len(
                      db.session.query(func.count(Show.start_time)).
                      filter(Show.artist_id == artist.id).
                      filter(datetimenow < Show.start_time).all()
                  )
          } for artist in artists
      ]
    }
    return render_template(
        'pages/search_artists.html',
        results=response,
        search_term=request.form.get('search_term', '')
        )


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    data = db.session.query(Artist).get(artist_id)
    data.past_shows = []
    past_shows = db.session.query(Show).\
        filter(
          Show.start_time < datetimenow,
          Show.artist_id == artist_id
        ).all()
    for past_show in past_shows:
        venue = db.session.query(Venue).get(past_show.venue_id)
        data.past_shows.append({
          "venue_id": venue.id,
          "venue_name": venue.name,
          "venue_image_link": venue.image_link,
          "start_time": past_show.start_time
        })
    data.upcoming_shows = []
    upcoming_shows = db.session.query(Show).\
        filter(
          Show.start_time > datetimenow,
          Show.artist_id == artist_id
        ).all()
    for upcoming_show in upcoming_shows:
        venue = db.session.query(Venue).get(upcoming_show.venue_id)
        data.upcoming_shows.append({
            "venue_id": venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": upcoming_show.start_time
        })
    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = db.session.query(Artist).get(artist_id)
    form = ArtistForm()
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    form.website_link.data = artist.website_link
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    artist = db.session.query(Artist).get(artist_id)
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form.getlist('genres')
    artist.facebook_link = request.form['facebook_link']
    artist.image_link = request.form['image_link']
    artist.website_link = request.form['website_link']
    artist.seeking_venue = 'seeking_venue' in request.form
    artist.seeking_description = request.form['seeking_description']
    db.session.commit()
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = db.session.query(Venue).get(venue_id)
    form = VenueForm()
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description
    form.image_link.data = venue.image_link
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue = db.session.query(Venue).get(venue_id)
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.genres = request.form.getlist('genres')
    venue.facebook_link = request.form['facebook_link']
    venue.image_link = request.form['image_link']
    venue.seeking_talent = 'seeking_talent' in request.form
    venue.seeking_description = request.form['seeking_description']
    db.session.commit()
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm()
    if form.validate_on_submit():
        try:
            newArtist = Artist(
              name=request.form['name'],
              city=request.form['city'],
              state=request.form['state'],
              phone=request.form['phone'],
              facebook_link=request.form['facebook_link'],
              genres=request.form.getlist('genres'),
              image_link=request.form['image_link'],
              website_link=request.form['website_link'],
              seeking_venue=request.form['seeking_venue'],
              seeking_description=request.form['seeking_description']
            )
            db.session.add(newArtist)
            db.session.commit()
            flash(
              'Artist ' +
              request.form['name'] +
              ' was successfully listed!', 'message')
        except BaseException:
            db.session.rollback()
            flash(
              'An error occurred. Artist ' +
              request.form['name'] +
              ' could not be listed.', 'error')
        finally:
            db.session.close()
        return render_template('pages/home.html')
    else:
        flash(
          'An error occurred. \
          Artist could not be validated. \
          Please use the right format.')
        flash( 
          form.errors
        )
        return render_template('forms/new_artist.html', form=form)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    shows = db.session.query(Show).all()
    data = []
    for show in shows:
        venue = db.session.query(Venue).get(show.venue_id)
        artist = db.session.query(Artist).get(show.artist_id)
        data.append({
            "venue_id": venue.id,
            "venue_name": venue.name,
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time,
            "show_id": show.id
        })
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm()
  if form.validate_on_submit():
      try:
          new_show = Show(
              artist_id=request.form['artist_id'],
              venue_id=request.form['venue_id'],
              start_time=request.form['start_time']
          )
          db.session.add(new_show)
          db.session.commit()
          flash('Show was successfully listed!', 'message')
      except BaseException:
          db.session.rollback()
          flash('An error occurred. Show could not be listed.', 'error')
          flash(
            form.errors
          )
      finally:
          db.session.close()
  return redirect(url_for('index'))


# Delete
# ------------------------------------
@app.route('/venues/<venue_id>/delete')
def delete_venue(venue_id):
    try:
        venue = db.session.query(Venue).filter_by(id=venue_id)
        venue_name = venue[0].name
        print(venue_name)
        venue.delete()
        db.session.commit()
        flash('Venue ' + venue_name + ' was successfully deleted!', 'massage')
    except BaseException:
        db.session.rollback()
        flash(
          'An error occurred. Venue ' +
          venue_name +
          ' could not be deleted.')
    finally:
        db.session.close()
    return redirect(url_for('index'))


@app.route('/artist/<artist_id>/delete')
def delete_artist(artist_id):
    try:
        artist = db.session.query(Artist).filter_by(id=artist_id)
        artist_name = artist[0].name
        artist.delete()
        db.session.commit()
        flash('Venue ' + artist_name + ' was successfully deleted!', 'massage')
    except BaseException:
        db.session.rollback()
        flash(
          'An error occurred. Venue ' +
          artist_name +
          ' could not be deleted.'
        )
    finally:
        db.session.close()
    return redirect(url_for('index'))


@app.route('/shows/<show_id>/delete')
def delete_show(show_id):
    try:
        show = db.session.query(Show).filter_by(id=show_id)
        show_id = str(show[0].id)
        show.delete()
        db.session.commit()
        flash('Venue ' + show_id + ' was successfully deleted!', 'massage')
    except BaseException:
        db.session.rollback()
        flash('An error occurred. Venue ' + show_id + ' could not be deleted.')
    finally:
        db.session.close()
    return redirect(url_for('index'))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s:\
            %(message)s \
            [in %(pathname)s:%(lineno)d]'
        )
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

if __name__ == '__main__':
    # port = int(os.environ.get('PORT', 6000))
    app.debug = True
    app.run(host='0.0.0.0', port=4000)
