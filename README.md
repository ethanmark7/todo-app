# Todo Application

A full-stack todo application built with Flask (backend) and vanilla JavaScript (frontend).

## Features

### Backend (Flask REST API)
- ✅ RESTful API with 6 endpoints
- ✅ SQLite database with SQLAlchemy ORM
- ✅ CORS enabled for frontend communication
- ✅ Input validation and error handling
- ✅ Standardized JSON responses

### Frontend (Vanilla JavaScript)
- ✅ Single page application
- ✅ Add, edit, delete, and toggle todos
- ✅ Real-time statistics (total, completed, pending)
- ✅ Modern, responsive UI design
- ✅ Toast notifications for user feedback

## Technology Stack

**Backend:**
- Flask 3.0.0
- Flask-SQLAlchemy 3.1.1
- Flask-CORS 4.0.0
- SQLite database

**Frontend:**
- HTML5
- CSS3
- Vanilla JavaScript (ES6+)

## Project Structure

```
todo-app/
├── backend/
│   ├── app.py              # Flask application & API routes
│   ├── models.py           # Database models
│   ├── config.py           # Configuration settings
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── index.html          # Main HTML file
│   ├── css/
│   │   └── styles.css      # Styling
│   └── js/
│       └── app.js          # Frontend logic
├── IMPLEMENTATION_PLAN.md  # Detailed implementation plan
└── README.md               # This file
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/todos` | Get all todos |
| GET | `/api/todos/:id` | Get single todo |
| POST | `/api/todos` | Create new todo |
| PUT | `/api/todos/:id` | Update todo |
| DELETE | `/api/todos/:id` | Delete todo |

### API Response Format

**Success Response:**
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional message"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error message",
  "status": 400
}
```

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation & Setup

### 1. Clone or Download the Project

```bash
cd /path/to/todo-app
```

### 2. Backend Setup

#### Create Virtual Environment (Recommended)

**macOS/Linux:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate
```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Frontend Setup

No installation required! The frontend uses vanilla JavaScript with no build process.

## Running the Application

You need to run both the backend and frontend servers simultaneously.

### Terminal 1: Start Backend Server

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python app.py
```

The backend API will be available at: **http://localhost:5050**

You should see:
```
 * Running on http://0.0.0.0:5050
 * Debug mode: on
```

### Terminal 2: Start Frontend Server

Open a new terminal window:

```bash
cd frontend
python -m http.server 8080
```

**Alternative (Python 2):**
```bash
python -m SimpleHTTPServer 8080
```

The frontend will be available at: **http://localhost:8080**

### 3. Access the Application

Open your web browser and navigate to:
```
http://localhost:8080
```

## Usage Guide

### Adding a Todo
1. Type your task in the input field
2. Click "Add Todo" or press Enter
3. The todo will appear in the list below

### Completing a Todo
- Click the checkbox next to a todo to mark it as complete
- Click again to mark it as incomplete

### Editing a Todo
1. Click the "Edit" button on a todo
2. Modify the text in the input field
3. Click "Save" or press Enter to save changes
4. Click "Cancel" or press Escape to discard changes

### Deleting a Todo
1. Click the "Delete" button on a todo
2. Confirm the deletion in the popup dialog

### Viewing Statistics
The statistics cards at the top show:
- **Total**: Total number of todos
- **Completed**: Number of completed todos
- **Pending**: Number of incomplete todos

## Database

The application uses SQLite database stored in `backend/todos.db`. The database is created automatically when you first run the backend server.

### Database Schema

**Todo Table:**
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key (auto-increment) |
| title | String(200) | Todo title |
| completed | Boolean | Completion status |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |

## Development

### Backend Development

The Flask app runs in debug mode by default, which means:
- Automatic reloading on code changes
- Detailed error messages
- Debug toolbar available

To disable debug mode, modify `app.py`:
```python
app.run(host='0.0.0.0', port=5050, debug=False)
```

### Frontend Development

The frontend uses vanilla JavaScript with no build process. Simply:
1. Edit the files in `frontend/`
2. Refresh your browser to see changes

## Troubleshooting

### Backend Issues

**Port 5050 already in use:**
```bash
# Find and kill the process using port 5050
# macOS/Linux:
lsof -ti:5050 | xargs kill -9

# Windows:
netstat -ano | findstr :5050
taskkill /PID <PID> /F
```

**Module not found errors:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

**Database errors:**
```bash
# Delete the database and restart
rm backend/todos.db
python app.py
```

### Frontend Issues

**CORS errors:**
- Ensure backend is running on port 5050
- Check that CORS is properly configured in `backend/config.py`

**Port 8080 already in use:**
```bash
# Use a different port
python -m http.server 8081

# Update API_BASE_URL in frontend/js/app.js if needed
```

**Cannot connect to backend:**
- Verify backend is running: `http://localhost:5050/api/health`
- Check browser console for error messages
- Ensure no firewall is blocking the connection

## Testing

### Manual API Testing

You can test the API endpoints using curl:

```bash
# Health check
curl http://localhost:5050/api/health

# Get all todos
curl http://localhost:5050/api/todos

# Create a todo
curl -X POST http://localhost:5050/api/todos \
  -H "Content-Type: application/json" \
  -d '{"title":"Test todo"}'

# Update a todo
curl -X PUT http://localhost:5050/api/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"completed":true}'

# Delete a todo
curl -X DELETE http://localhost:5050/api/todos/1
```

### Browser Testing

1. Open the application in your browser
2. Open Developer Tools (F12)
3. Check the Console tab for any errors
4. Use the Network tab to monitor API requests

## Production Deployment

For production deployment, consider:

1. **Backend:**
   - Use a production WSGI server (Gunicorn, uWSGI)
   - Set `debug=False` in app.py
   - Use environment variables for configuration
   - Use PostgreSQL or MySQL instead of SQLite
   - Implement authentication and authorization

2. **Frontend:**
   - Serve static files through a web server (Nginx, Apache)
   - Update API_BASE_URL to production backend URL
   - Implement proper error boundaries
   - Add loading states

## License

This project is open source and available for educational purposes.

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review the IMPLEMENTATION_PLAN.md for architecture details
3. Check browser console and backend logs for errors

---

**Happy Todo Managing! 📝✨**