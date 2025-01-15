from flask import render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db, login_manager
from models import User, Location, Itinerary, ItineraryStop, Badge
from datetime import datetime

@login_manager.user_loader
def load_user(id):
    return db.session.get(User, int(id))

def init_badges():
    """Initialize default badges if they don't exist"""
    default_badges = [
        # Places visited badges
        {'name': 'First Step', 'description': 'Visit your first place', 'badge_type': 'places', 'requirement': 1,
         'icon': 'footprints'},
        {'name': 'Explorer', 'description': 'Visit 5 different places', 'badge_type': 'places', 'requirement': 5,
         'icon': 'compass'},
        {'name': 'Adventurer', 'description': 'Visit 10 different places', 'badge_type': 'places', 'requirement': 10,
         'icon': 'map'},
        {'name': 'Voyager', 'description': 'Visit 25 different places', 'badge_type': 'places', 'requirement': 25,
         'icon': 'globe'},
        {'name': 'World Traveler', 'description': 'Visit 50 different places', 'badge_type': 'places', 'requirement': 50,
         'icon': 'earth'},

        # Countries badges
        {'name': 'First Country', 'description': 'Visit your first country', 'badge_type': 'countries', 'requirement': 1,
         'icon': 'flag'},
        {'name': 'Globe Trotter', 'description': 'Visit 3 different countries', 'badge_type': 'countries', 'requirement': 3,
         'icon': 'world'},
        {'name': 'World Explorer', 'description': 'Visit 5 different countries', 'badge_type': 'countries', 'requirement': 5,
         'icon': 'earth-americas'},
        {'name': 'Continental', 'description': 'Visit 10 different countries', 'badge_type': 'countries', 'requirement': 10,
         'icon': 'globe-americas'},
        {'name': 'World Citizen', 'description': 'Visit 20 different countries', 'badge_type': 'countries', 'requirement': 20,
         'icon': 'earth-europe'},

        # Social badges
        {'name': 'First Follower', 'description': 'Get your first follower', 'badge_type': 'social', 'requirement': 1,
         'icon': 'user-plus'},
        {'name': 'Rising Star', 'description': 'Get 10 followers', 'badge_type': 'social', 'requirement': 10,
         'icon': 'users'},
        {'name': 'Travel Influencer', 'description': 'Get 50 followers', 'badge_type': 'social', 'requirement': 50,
         'icon': 'trending-up'},
        {'name': 'Travel Celebrity', 'description': 'Get 100 followers', 'badge_type': 'social', 'requirement': 100,
         'icon': 'award'}
    ]

    for badge_data in default_badges:
        if not Badge.query.filter_by(name=badge_data['name']).first():
            badge = Badge(
                name=badge_data['name'],
                description=badge_data['description'],
                badge_type=badge_data['badge_type'],
                requirement=badge_data['requirement'],
                icon=f"feather-{badge_data['icon']}"
            )
            db.session.add(badge)

    db.session.commit()

# Initialize badges
with app.app_context():
    init_badges()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid email or password')
    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        if User.query.filter_by(email=request.form['email']).first():
            flash('Email already registered')
            return redirect(url_for('register'))

        user = User(
            username=request.form['username'],
            email=request.form['email']
        )
        user.set_password(request.form['password'])
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('index'))
    return render_template('auth/register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    current_user.check_and_award_badges()
    db.session.commit()
    return render_template('profile.html')

@app.route('/locations', methods=['GET', 'POST'])
@login_required
def locations():
    if request.method == 'POST':
        # Add country extraction from the location name using the Nominatim API
        location = Location(
            user_id=current_user.id,
            name=request.form['name'],
            country=request.form.get('country'),
            latitude=float(request.form['latitude']),
            longitude=float(request.form['longitude']),
            rating=int(request.form['rating']),
            description=request.form['description'],
            image_url=f"https://source.unsplash.com/800x600/?{request.form['name'].replace(' ', '+')},city"
        )
        db.session.add(location)
        db.session.commit()

        # Check for new badges
        current_user.check_and_award_badges()
        db.session.commit()

        return redirect(url_for('locations'))

    locations = Location.query.filter_by(user_id=current_user.id).all()
    return render_template('locations.html', locations=locations)

@app.route('/api/locations', methods=['GET'])
def get_locations():
    locations = Location.query.all()
    return jsonify([{
        'id': loc.id,
        'name': loc.name,
        'latitude': loc.latitude,
        'longitude': loc.longitude,
        'rating': loc.rating,
        'image_url': loc.image_url
    } for loc in locations])

@app.route('/itineraries')
@login_required
def itineraries():
    user_itineraries = Itinerary.query.filter_by(user_id=current_user.id).all()
    return render_template('itineraries/index.html', itineraries=user_itineraries)

@app.route('/itineraries/new', methods=['GET', 'POST'])
@login_required
def new_itinerary():
    if request.method == 'POST':
        itinerary = Itinerary(
            user_id=current_user.id,
            title=request.form['title'],
            description=request.form['description'],
            start_date=datetime.strptime(request.form['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        )
        db.session.add(itinerary)
        db.session.commit()
        return redirect(url_for('edit_itinerary', id=itinerary.id))
    return render_template('itineraries/new.html')

@app.route('/itineraries/<int:id>')
@login_required
def view_itinerary(id):
    itinerary = Itinerary.query.get_or_404(id)
    if itinerary.user_id != current_user.id:
        flash('Access denied')
        return redirect(url_for('itineraries'))
    return render_template('itineraries/view.html', itinerary=itinerary)

@app.route('/itineraries/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_itinerary(id):
    itinerary = Itinerary.query.get_or_404(id)
    if itinerary.user_id != current_user.id:
        flash('Access denied')
        return redirect(url_for('itineraries'))

    if request.method == 'POST':
        itinerary.title = request.form['title']
        itinerary.description = request.form['description']
        itinerary.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        itinerary.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        db.session.commit()
        return redirect(url_for('view_itinerary', id=itinerary.id))

    return render_template('itineraries/edit.html', itinerary=itinerary)

@app.route('/itineraries/<int:id>/stops', methods=['POST'])
@login_required
def add_stop(id):
    itinerary = Itinerary.query.get_or_404(id)
    if itinerary.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403

    stop = ItineraryStop(
        itinerary_id=id,
        location_id=request.form['location_id'],
        day_number=request.form['day_number'],
        notes=request.form.get('notes', '')
    )
    db.session.add(stop)
    db.session.commit()
    return redirect(url_for('edit_itinerary', id=id))

@app.route('/itineraries/<int:itinerary_id>/stops/<int:stop_id>', methods=['DELETE'])
@login_required
def remove_stop(itinerary_id, stop_id):
    stop = ItineraryStop.query.get_or_404(stop_id)
    if stop.itinerary.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403

    db.session.delete(stop)
    db.session.commit()
    return '', 204

@app.route('/users/<username>')
@login_required
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user_profile.html', user=user)

@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User not found.')
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user_profile', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(f'You are now following {username}!')
    return redirect(url_for('user_profile', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User not found.')
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user_profile', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(f'You have unfollowed {username}.')
    return redirect(url_for('user_profile', username=username))

@app.route('/users')
@login_required
def users():
    users = User.query.filter(User.id != current_user.id).all()
    return render_template('users.html', users=users)