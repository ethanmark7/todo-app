"""
Flask REST API for Todo application
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from config import Config
from models import db, Todo

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
CORS(app, origins=Config.CORS_ORIGINS)

# Create database tables
with app.app_context():
    db.create_all()


def success_response(data=None, message=None, status=200):
    """Create a standardized success response"""
    response = {'success': True}
    if data is not None:
        response['data'] = data
    if message:
        response['message'] = message
    return jsonify(response), status


def error_response(error, status=400):
    """Create a standardized error response"""
    return jsonify({
        'success': False,
        'error': error,
        'status': status
    }), status


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return success_response({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/todos', methods=['GET'])
def get_todos():
    """Get all todos"""
    try:
        todos = Todo.query.order_by(Todo.created_at.desc()).all()
        return success_response(
            data=[todo.to_dict() for todo in todos],
            message=f'Retrieved {len(todos)} todos'
        )
    except Exception as e:
        return error_response(f'Failed to retrieve todos: {str(e)}', 500)


@app.route('/api/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    """Get a single todo by ID"""
    try:
        todo = Todo.query.get(todo_id)
        if not todo:
            return error_response(f'Todo with id {todo_id} not found', 404)
        return success_response(data=todo.to_dict())
    except Exception as e:
        return error_response(f'Failed to retrieve todo: {str(e)}', 500)


@app.route('/api/todos', methods=['POST'])
def create_todo():
    """Create a new todo"""
    try:
        data = request.get_json(force=True, silent=True)
        
        # Validate input
        if data is None:
            return error_response('Request body is required', 400)
        
        title = data.get('title', '').strip()
        if not title:
            return error_response('Title is required', 400)
        
        if len(title) > 200:
            return error_response('Title must be 200 characters or less', 400)
        
        # Create new todo
        todo = Todo(title=title)
        db.session.add(todo)
        db.session.commit()
        
        return success_response(
            data=todo.to_dict(),
            message='Todo created successfully',
            status=201
        )
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create todo: {str(e)}', 500)


@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """Update an existing todo"""
    try:
        todo = Todo.query.get(todo_id)
        if not todo:
            return error_response(f'Todo with id {todo_id} not found', 404)
        
        data = request.get_json(force=True, silent=True)
        if data is None:
            return error_response('Request body is required', 400)
        
        # Update title if provided
        if 'title' in data:
            title = data['title'].strip()
            if not title:
                return error_response('Title cannot be empty', 400)
            if len(title) > 200:
                return error_response('Title must be 200 characters or less', 400)
            todo.title = title
        
        # Update completed status if provided
        if 'completed' in data:
            if not isinstance(data['completed'], bool):
                return error_response('Completed must be a boolean', 400)
            todo.completed = data['completed']
        
        # Update timestamp
        todo.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return success_response(
            data=todo.to_dict(),
            message='Todo updated successfully'
        )
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update todo: {str(e)}', 500)


@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """Delete a todo"""
    try:
        todo = Todo.query.get(todo_id)
        if not todo:
            return error_response(f'Todo with id {todo_id} not found', 404)
        
        db.session.delete(todo)
        db.session.commit()
        
        return success_response(message=f'Todo {todo_id} deleted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete todo: {str(e)}', 500)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)

# Made with Bob
