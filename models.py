from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Association table for followers
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

# Association table for user badges
user_badges = db.Table('user_badges',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('badge_id', db.Integer, db.ForeignKey('badge.id'))
)

class Badge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(256))
    icon = db.Column(db.String(128))  # SVG icon path
    badge_type = db.Column(db.String(64))  # e.g., 'places', 'countries', 'ratings', 'social'
    requirement = db.Column(db.Integer)  # Number required to earn the badge
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    locations = db.relationship('Location', backref='user', lazy=True)
    itineraries = db.relationship('Itinerary', backref='user', lazy=True)
    badges = db.relationship('Badge', secondary=user_badges, backref='users', lazy='dynamic')

    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def check_and_award_badges(self):
        places_count = len(self.locations)
        for threshold in [1, 5, 10, 25, 50]:
            if places_count >= threshold:
                badge = Badge.query.filter_by(
                    badge_type='places', 
                    requirement=threshold
                ).first()
                if badge and badge not in self.badges:
                    self.badges.append(badge)

        countries = set(loc.country for loc in self.locations if loc.country)
        countries_count = len(countries)
        for threshold in [1, 3, 5, 10, 20]:
            if countries_count >= threshold:
                badge = Badge.query.filter_by(
                    badge_type='countries', 
                    requirement=threshold
                ).first()
                if badge and badge not in self.badges:
                    self.badges.append(badge)

        followers_count = self.followers.count()
        for threshold in [1, 10, 50, 100]:
            if followers_count >= threshold:
                badge = Badge.query.filter_by(
                    badge_type='social', 
                    requirement=threshold
                ).first()
                if badge and badge not in self.badges:
                    self.badges.append(badge)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(64), nullable=False)  # e.g., 'accommodation', 'food', 'transport', 'activities'
    description = db.Column(db.String(256))
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    currency = db.Column(db.String(3), nullable=False, default='USD')  # ISO currency code
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    country = db.Column(db.String(64))
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    rating = db.Column(db.Integer)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    visited_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    itinerary_stops = db.relationship('ItineraryStop', backref='location', lazy=True)
    expenses = db.relationship('Expense', backref='location', lazy=True, cascade='all, delete-orphan')

    def get_expense_summary(self):
        total = 0
        by_category = {}

        for expense in self.expenses:
            total += expense.amount
            if expense.category not in by_category:
                by_category[expense.category] = 0
            by_category[expense.category] += expense.amount

        return {
            'total': round(total, 2),
            'by_category': {k: round(v, 2) for k, v in by_category.items()},
            'currency': self.expenses[0].currency if self.expenses else 'USD'
        }

class Itinerary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    stops = db.relationship('ItineraryStop', backref='itinerary', lazy=True, order_by='ItineraryStop.day_number')

class ItineraryStop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    itinerary_id = db.Column(db.Integer, db.ForeignKey('itinerary.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    day_number = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)