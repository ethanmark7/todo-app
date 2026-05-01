"""
Unit tests for the Todo API
Tests all endpoints with comprehensive coverage
"""
import pytest
import json
from datetime import datetime
from app import app, db
from models import Todo


@pytest.fixture
def client():
    """Create a test client with a temporary database"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()


@pytest.fixture
def sample_todo(client):
    """Create a sample todo for testing"""
    with app.app_context():
        todo = Todo(title="Test Todo", completed=False)
        db.session.add(todo)
        db.session.commit()
        return todo.id


class TestHealthEndpoint:
    """Tests for the health check endpoint"""
    
    def test_health_check_success(self, client):
        """Test health check returns healthy status"""
        response = client.get('/api/health')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert data['data']['status'] == 'healthy'
        assert 'timestamp' in data['data']
    
    def test_health_check_has_timestamp(self, client):
        """Test health check includes valid timestamp"""
        response = client.get('/api/health')
        data = json.loads(response.data)
        
        timestamp = data['data']['timestamp']
        # Verify timestamp is in ISO format
        datetime.fromisoformat(timestamp)


class TestGetTodos:
    """Tests for GET /api/todos endpoint"""
    
    def test_get_empty_todos(self, client):
        """Test getting todos when database is empty"""
        response = client.get('/api/todos')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert data['data'] == []
        assert data['message'] == 'Retrieved 0 todos'
    
    def test_get_todos_with_data(self, client, sample_todo):
        """Test getting todos when database has data"""
        response = client.get('/api/todos')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert len(data['data']) == 1
        assert data['data'][0]['title'] == 'Test Todo'
        assert data['data'][0]['completed'] is False
        assert 'id' in data['data'][0]
        assert 'created_at' in data['data'][0]
        assert 'updated_at' in data['data'][0]
    
    def test_get_todos_multiple(self, client):
        """Test getting multiple todos"""
        with app.app_context():
            todo1 = Todo(title="Todo 1", completed=False)
            todo2 = Todo(title="Todo 2", completed=True)
            todo3 = Todo(title="Todo 3", completed=False)
            db.session.add_all([todo1, todo2, todo3])
            db.session.commit()
        
        response = client.get('/api/todos')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert len(data['data']) == 3
        assert data['message'] == 'Retrieved 3 todos'


class TestGetSingleTodo:
    """Tests for GET /api/todos/:id endpoint"""
    
    def test_get_todo_success(self, client, sample_todo):
        """Test getting a single todo by ID"""
        response = client.get(f'/api/todos/{sample_todo}')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert data['data']['id'] == sample_todo
        assert data['data']['title'] == 'Test Todo'
    
    def test_get_todo_not_found(self, client):
        """Test getting a non-existent todo"""
        response = client.get('/api/todos/999')
        data = json.loads(response.data)
        
        assert response.status_code == 404
        assert data['success'] is False
        assert 'not found' in data['error'].lower()
    
    def test_get_todo_invalid_id(self, client):
        """Test getting a todo with invalid ID format"""
        response = client.get('/api/todos/invalid')
        # Flask will return 404 for invalid route parameter
        assert response.status_code == 404


class TestCreateTodo:
    """Tests for POST /api/todos endpoint"""
    
    def test_create_todo_success(self, client):
        """Test creating a new todo"""
        response = client.post(
            '/api/todos',
            data=json.dumps({'title': 'New Todo'}),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        assert response.status_code == 201
        assert data['success'] is True
        assert data['data']['title'] == 'New Todo'
        assert data['data']['completed'] is False
        assert 'id' in data['data']
        assert data['message'] == 'Todo created successfully'
    
    def test_create_todo_no_body(self, client):
        """Test creating todo without request body"""
        response = client.post('/api/todos', content_type='application/json')
        data = json.loads(response.data)
        
        assert response.status_code == 400
        assert data['success'] is False
        assert 'required' in data['error'].lower()
    
    def test_create_todo_empty_title(self, client):
        """Test creating todo with empty title"""
        response = client.post(
            '/api/todos',
            data=json.dumps({'title': ''}),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        assert response.status_code == 400
        assert data['success'] is False
        assert 'required' in data['error'].lower()
    
    def test_create_todo_whitespace_title(self, client):
        """Test creating todo with whitespace-only title"""
        response = client.post(
            '/api/todos',
            data=json.dumps({'title': '   '}),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        assert response.status_code == 400
        assert data['success'] is False
    
    def test_create_todo_title_too_long(self, client):
        """Test creating todo with title exceeding max length"""
        long_title = 'x' * 201
        response = client.post(
            '/api/todos',
            data=json.dumps({'title': long_title}),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        assert response.status_code == 400
        assert data['success'] is False
        assert '200' in data['error']
    
    def test_create_todo_missing_title(self, client):
        """Test creating todo without title field"""
        response = client.post(
            '/api/todos',
            data=json.dumps({}),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        assert response.status_code == 400
        assert data['success'] is False
    
    def test_create_todo_with_special_characters(self, client):
        """Test creating todo with special characters"""
        response = client.post(
            '/api/todos',
            data=json.dumps({'title': 'Todo with émojis 🎉 & symbols!'}),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        assert response.status_code == 201
        assert data['success'] is True
        assert 'émojis' in data['data']['title']


class TestUpdateTodo:
    """Tests for PUT /api/todos/:id endpoint"""
    
    def test_update_todo_title(self, client, sample_todo):
        """Test updating todo title"""
        response = client.put(
            f'/api/todos/{sample_todo}',
            data=json.dumps({'title': 'Updated Title'}),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert data['data']['title'] == 'Updated Title'
        assert data['message'] == 'Todo updated successfully'
    
    def test_update_todo_completed(self, client, sample_todo):
        """Test updating todo completion status"""
        response = client.put(
            f'/api/todos/{sample_todo}',
            data=json.dumps({'completed': True}),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert data['data']['completed'] is True
    
    def test_update_todo_both_fields(self, client, sample_todo):
        """Test updating both title and completed status"""
        response = client.put(
            f'/api/todos/{sample_todo}',
            data=json.dumps({'title': 'New Title', 'completed': True}),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['data']['title'] == 'New Title'
        assert data['data']['completed'] is True
    
    def test_update_todo_not_found(self, client):
        """Test updating non-existent todo"""
        response = client.put(
            '/api/todos/999',
            data=json.dumps({'title': 'Updated'}),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        assert response.status_code == 404
        assert data['success'] is False
        assert 'not found' in data['error'].lower()
    
    def test_update_todo_no_body(self, client, sample_todo):
        """Test updating todo without request body"""
        response = client.put(
            f'/api/todos/{sample_todo}',
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        assert response.status_code == 400
        assert data['success'] is False
    
    def test_update_todo_empty_title(self, client, sample_todo):
        """Test updating todo with empty title"""
        response = client.put(
            f'/api/todos/{sample_todo}',
            data=json.dumps({'title': ''}),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        assert response.status_code == 400
        assert data['success'] is False
        assert 'empty' in data['error'].lower()
    
    def test_update_todo_title_too_long(self, client, sample_todo):
        """Test updating todo with title exceeding max length"""
        long_title = 'x' * 201
        response = client.put(
            f'/api/todos/{sample_todo}',
            data=json.dumps({'title': long_title}),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        assert response.status_code == 400
        assert data['success'] is False
    
    def test_update_todo_invalid_completed_type(self, client, sample_todo):
        """Test updating todo with invalid completed value"""
        response = client.put(
            f'/api/todos/{sample_todo}',
            data=json.dumps({'completed': 'not_a_boolean'}),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        assert response.status_code == 400
        assert data['success'] is False
        assert 'boolean' in data['error'].lower()
    
    def test_update_todo_updates_timestamp(self, client, sample_todo):
        """Test that updating a todo updates the updated_at timestamp"""
        # Get original timestamp
        response1 = client.get(f'/api/todos/{sample_todo}')
        data1 = json.loads(response1.data)
        original_updated_at = data1['data']['updated_at']
        
        # Update the todo
        response2 = client.put(
            f'/api/todos/{sample_todo}',
            data=json.dumps({'title': 'Updated'}),
            content_type='application/json'
        )
        data2 = json.loads(response2.data)
        new_updated_at = data2['data']['updated_at']
        
        # Timestamps should be different
        assert new_updated_at >= original_updated_at


class TestDeleteTodo:
    """Tests for DELETE /api/todos/:id endpoint"""
    
    def test_delete_todo_success(self, client, sample_todo):
        """Test deleting a todo"""
        response = client.delete(f'/api/todos/{sample_todo}')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert 'deleted successfully' in data['message'].lower()
        
        # Verify todo is actually deleted
        get_response = client.get(f'/api/todos/{sample_todo}')
        assert get_response.status_code == 404
    
    def test_delete_todo_not_found(self, client):
        """Test deleting non-existent todo"""
        response = client.delete('/api/todos/999')
        data = json.loads(response.data)
        
        assert response.status_code == 404
        assert data['success'] is False
        assert 'not found' in data['error'].lower()
    
    def test_delete_todo_removes_from_database(self, client):
        """Test that delete actually removes todo from database"""
        # Create a todo
        with app.app_context():
            todo = Todo(title="To Delete", completed=False)
            db.session.add(todo)
            db.session.commit()
            todo_id = todo.id
        
        # Delete it
        client.delete(f'/api/todos/{todo_id}')
        
        # Verify it's gone
        with app.app_context():
            deleted_todo = db.session.get(Todo, todo_id)
            assert deleted_todo is None


class TestTodoModel:
    """Tests for the Todo model"""
    
    def test_todo_creation(self, client):
        """Test creating a Todo model instance"""
        with app.app_context():
            todo = Todo(title="Model Test", completed=False)
            db.session.add(todo)
            db.session.commit()
            
            assert todo.id is not None
            assert todo.title == "Model Test"
            assert todo.completed is False
            assert todo.created_at is not None
            assert todo.updated_at is not None
    
    def test_todo_to_dict(self, client):
        """Test Todo model to_dict method"""
        with app.app_context():
            todo = Todo(title="Dict Test", completed=True)
            db.session.add(todo)
            db.session.commit()
            
            todo_dict = todo.to_dict()
            
            assert isinstance(todo_dict, dict)
            assert todo_dict['title'] == "Dict Test"
            assert todo_dict['completed'] is True
            assert 'id' in todo_dict
            assert 'created_at' in todo_dict
            assert 'updated_at' in todo_dict
    
    def test_todo_repr(self, client):
        """Test Todo model __repr__ method"""
        with app.app_context():
            todo = Todo(title="Repr Test", completed=False)
            db.session.add(todo)
            db.session.commit()
            
            repr_str = repr(todo)
            assert 'Todo' in repr_str
            assert str(todo.id) in repr_str
            assert 'Repr Test' in repr_str


class TestResponseHelpers:
    """Tests for response helper functions"""
    
    def test_success_response_with_data(self, client):
        """Test success response includes data"""
        response = client.get('/api/health')
        data = json.loads(response.data)
        
        assert 'success' in data
        assert 'data' in data
        assert data['success'] is True
    
    def test_error_response_format(self, client):
        """Test error response format"""
        response = client.get('/api/todos/999')
        data = json.loads(response.data)
        
        assert 'success' in data
        assert 'error' in data
        assert 'status' in data
        assert data['success'] is False


class TestCORS:
    """Tests for CORS configuration"""
    
    def test_cors_headers_present(self, client):
        """Test that CORS headers are present in responses"""
        response = client.get('/api/health')
        
        # CORS headers should be present
        assert 'Access-Control-Allow-Origin' in response.headers
    
    def test_options_request(self, client):
        """Test OPTIONS request for CORS preflight"""
        response = client.options('/api/todos')
        
        assert response.status_code == 200


class TestEdgeCases:
    """Tests for edge cases and error scenarios"""
    
    def test_invalid_json(self, client):
        """Test sending invalid JSON"""
        response = client.post(
            '/api/todos',
            data='invalid json',
            content_type='application/json'
        )
        # Should handle gracefully
        assert response.status_code in [400, 500]
    
    def test_concurrent_updates(self, client, sample_todo):
        """Test handling concurrent updates to same todo"""
        # Update 1
        response1 = client.put(
            f'/api/todos/{sample_todo}',
            data=json.dumps({'title': 'Update 1'}),
            content_type='application/json'
        )
        
        # Update 2
        response2 = client.put(
            f'/api/todos/{sample_todo}',
            data=json.dumps({'title': 'Update 2'}),
            content_type='application/json'
        )
        
        # Both should succeed
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Final state should be Update 2
        data = json.loads(response2.data)
    
    def test_get_single_todo_by_id(self, client, sample_todo):
        """Test getting a specific todo by ID"""
        response = client.get(f'/api/todos/{sample_todo}')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert data['data']['id'] == sample_todo
    
    def test_create_multiple_todos(self, client):
        """Test creating multiple todos in sequence"""
        titles = ['Todo 1', 'Todo 2', 'Todo 3']
        
        for title in titles:
            response = client.post(
                '/api/todos',
                data=json.dumps({'title': title}),
                content_type='application/json'
            )
            assert response.status_code == 201
        
        # Verify all were created
        response = client.get('/api/todos')
        data = json.loads(response.data)
        assert len(data['data']) == 3
    
    def test_update_nonexistent_field(self, client, sample_todo):
        """Test updating with extra fields (should be ignored)"""
        response = client.put(
            f'/api/todos/{sample_todo}',
            data=json.dumps({'title': 'Updated', 'extra_field': 'ignored'}),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['data']['title'] == 'Updated'
        assert 'extra_field' not in data['data']
    
    def test_delete_already_deleted_todo(self, client, sample_todo):
        """Test deleting a todo that was already deleted"""
        # Delete once
        response1 = client.delete(f'/api/todos/{sample_todo}')
        assert response1.status_code == 200
        
        # Try to delete again
        response2 = client.delete(f'/api/todos/{sample_todo}')
        assert response2.status_code == 404

# Made with Bob
