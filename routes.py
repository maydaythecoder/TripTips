from flask import render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db, login_manager
from models import User, Location, Itinerary, ItineraryStop
from datetime import datetime

@login_manager.user_loader
def load_user(id):
    return db.session.get(User, int(id))

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
    return render_template('profile.html')

@app.route('/locations', methods=['GET', 'POST'])
@login_required
def locations():
    if request.method == 'POST':
        location = Location(
            user_id=current_user.id,
            name=request.form['name'],
            latitude=float(request.form['latitude']),
            longitude=float(request.form['longitude']),
            rating=int(request.form['rating']),
            description=request.form['description']
        )
        db.session.add(location)
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
        'rating': loc.rating
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