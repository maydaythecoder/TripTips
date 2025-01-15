# TravelTips

A comprehensive web-based travel platform that enables users to track, plan, and discover travel experiences through interactive mapping and social networking features.

## Features

- 🗺️ Interactive travel mapping with OpenStreetMap integration
- 📍 Location tracking and rating system
- 💰 Trip expense tracking and summaries
- ✈️ Travel itinerary planning
- 🏆 Achievement badge system
- 👥 Social following system
- 📱 Responsive design with Bootstrap dark theme

## Tech Stack

- **Backend**: Flask web framework
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: Flask-Login
- **Frontend**: Bootstrap with dark theme
- **Maps**: Leaflet.js with OpenStreetMap
- **Icons**: Feather Icons

## Project Structure

```
├── app.py                 # Flask application initialization
├── main.py               # Application entry point
├── models.py             # Database models
├── routes.py             # Application routes and views
├── static/               # Static assets
│   ├── css/             # CSS stylesheets
│   │   └── custom.css   # Custom styling
│   └── js/              # JavaScript files
│       ├── map.js       # Map functionality
│       └── ratings.js   # Rating system
├── templates/           # Jinja2 templates
│   ├── auth/           # Authentication templates
│   ├── itineraries/    # Travel planning templates
│   ├── locations/      # Location management templates
│   └── base.html       # Base template
```

## Setup Instructions

1. **Prerequisites**
   - Python 3.11 or higher
   - PostgreSQL database
   - VSCode or Cursor editor

2. **Environment Setup**
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Database Configuration**
   - Set up PostgreSQL database
   - Configure DATABASE_URL in environment variables

4. **Running the Application**
   ```bash
   python main.py
   ```
   The application will be available at `http://localhost:5000`

## Editor Setup

### VSCode Setup
1. **Install VSCode Extensions**
   - Python (Microsoft)
   - Python IntelliSense
   - SQLTools (PostgreSQL/Cockroach driver)
   - GitLens (optional)

2. **Configure Python Environment**
   ```json
   // .vscode/settings.json
   {
     "python.defaultInterpreterPath": "/path/to/python3.11",
     "python.linting.enabled": true,
     "python.linting.pylintEnabled": true,
     "python.formatting.provider": "black"
   }
   ```

3. **Debug Configuration**
   ```json
   // .vscode/launch.json
   {
     "version": "0.2.0",
     "configurations": [
       {
         "name": "Flask",
         "type": "python",
         "request": "launch",
         "module": "flask",
         "env": {
           "FLASK_APP": "main.py",
           "FLASK_DEBUG": "1"
         },
         "args": [
           "run",
           "--host=0.0.0.0",
           "--port=5000"
         ],
         "jinja": true
       }
     ]
   }
   ```

### Cursor Setup
1. **Initial Setup**
   - Install Cursor from [cursor.so](https://cursor.so)
   - Open the project folder in Cursor

2. **Configure Python Environment**
   - Open Command Palette (Cmd/Ctrl + Shift + P)
   - Select "Python: Select Interpreter"
   - Choose Python 3.11

3. **Debug Configuration**
   - Click the "Run and Debug" icon in the sidebar
   - Create a `launch.json` file with the same configuration as VSCode above

4. **Recommended Settings**
   - Enable "Format on Save"
   - Set Black as the Python formatter
   - Enable "Auto Import"


## Features in Detail

### Location Management
- Add new locations with geocoding support
- Rate and review visited places
- Upload location photos
- Track expenses per location

### Travel Planning
- Create detailed travel itineraries
- Add multiple stops to each itinerary
- Set dates and add notes for each stop
- View itinerary on interactive map

### Social Features
- Follow other travelers
- View their travel histories
- Share travel experiences
- Build a travel community

### Achievement System
- Earn badges for travel milestones
- Track progress across different categories
- Unlock new achievements through activity

### Expense Tracking
- Add expenses per location
- Categorize spending
- Support multiple currencies
- Generate expense summaries

## Database Schema

### Core Tables
- `user`: User accounts and profiles
- `location`: Visited places and details
- `itinerary`: Travel plans
- `itinerary_stop`: Individual stops in an itinerary
- `expense`: Location-specific expenses
- `badge`: Achievement system
- `user_badges`: User-badge associations
- `followers`: Social following relationships

## API Endpoints

### Authentication
- `POST /login`: User login
- `POST /register`: New user registration
- `GET /logout`: User logout

### Locations
- `GET /locations`: List user's locations
- `POST /locations`: Add new location
- `GET /locations/<id>`: View location details
- `POST /locations/<id>/expenses`: Add expense

### Itineraries
- `GET /itineraries`: List travel plans
- `POST /itineraries`: Create new itinerary
- `GET /itineraries/<id>`: View itinerary
- `POST /itineraries/<id>/stops`: Add itinerary stop

### Social
- `GET /users`: View community members
- `GET /users/<username>`: View user profile
- `GET /follow/<username>`: Follow user
- `GET /unfollow/<username>`: Unfollow user

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.