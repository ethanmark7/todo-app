/**
 * Todo Application - Frontend JavaScript
 * Handles all client-side logic and API communication
 */

const API_BASE_URL = 'http://localhost:5050/api';

// State management
let todos = [];
let editingTodoId = null;

// DOM Elements
const todoForm = document.getElementById('add-todo-form');
const todoInput = document.getElementById('todo-input');
const todosList = document.getElementById('todos-list');
const emptyState = document.getElementById('empty-state');
const totalCount = document.getElementById('total-count');
const completedCount = document.getElementById('completed-count');
const pendingCount = document.getElementById('pending-count');
const toast = document.getElementById('toast');

/**
 * API Client Functions
 */

// Fetch all todos
async function fetchTodos() {
    try {
        const response = await fetch(`${API_BASE_URL}/todos`);
        const data = await response.json();
        
        if (data.success) {
            todos = data.data;
            renderTodos();
            updateStatistics();
        } else {
            showToast('Failed to load todos', 'error');
        }
    } catch (error) {
        showToast('Error connecting to server', 'error');
        console.error('Error fetching todos:', error);
    }
}

// Create a new todo
async function createTodo(title) {
    try {
        const response = await fetch(`${API_BASE_URL}/todos`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ title }),
        });
        
        const data = await response.json();
        
        if (data.success) {
            todos.unshift(data.data);
            renderTodos();
            updateStatistics();
            showToast('Todo added successfully', 'success');
            return true;
        } else {
            showToast(data.error || 'Failed to create todo', 'error');
            return false;
        }
    } catch (error) {
        showToast('Error creating todo', 'error');
        console.error('Error creating todo:', error);
        return false;
    }
}

// Update a todo
async function updateTodo(id, updates) {
    try {
        const response = await fetch(`${API_BASE_URL}/todos/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(updates),
        });
        
        const data = await response.json();
        
        if (data.success) {
            const index = todos.findIndex(todo => todo.id === id);
            if (index !== -1) {
                todos[index] = data.data;
                renderTodos();
                updateStatistics();
            }
            showToast('Todo updated successfully', 'success');
            return true;
        } else {
            showToast(data.error || 'Failed to update todo', 'error');
            return false;
        }
    } catch (error) {
        showToast('Error updating todo', 'error');
        console.error('Error updating todo:', error);
        return false;
    }
}

// Delete a todo
async function deleteTodo(id) {
    try {
        const response = await fetch(`${API_BASE_URL}/todos/${id}`, {
            method: 'DELETE',
        });
        
        const data = await response.json();
        
        if (data.success) {
            todos = todos.filter(todo => todo.id !== id);
            renderTodos();
            updateStatistics();
            showToast('Todo deleted successfully', 'success');
            return true;
        } else {
            showToast(data.error || 'Failed to delete todo', 'error');
            return false;
        }
    } catch (error) {
        showToast('Error deleting todo', 'error');
        console.error('Error deleting todo:', error);
        return false;
    }
}

/**
 * UI Rendering Functions
 */

// Render all todos
function renderTodos() {
    todosList.innerHTML = '';
    
    if (todos.length === 0) {
        emptyState.classList.remove('hidden');
        return;
    }
    
    emptyState.classList.add('hidden');
    
    todos.forEach(todo => {
        const todoElement = createTodoElement(todo);
        todosList.appendChild(todoElement);
    });
}

// Create a single todo element
function createTodoElement(todo) {
    const div = document.createElement('div');
    div.className = `todo-item ${todo.completed ? 'completed' : ''}`;
    div.dataset.id = todo.id;
    
    const isEditing = editingTodoId === todo.id;
    
    div.innerHTML = `
        <input 
            type="checkbox" 
            class="todo-checkbox" 
            ${todo.completed ? 'checked' : ''}
            onchange="toggleTodo(${todo.id})"
        >
        <div class="todo-content">
            ${isEditing ? `
                <input 
                    type="text" 
                    class="todo-title-input" 
                    value="${escapeHtml(todo.title)}"
                    id="edit-input-${todo.id}"
                    maxlength="200"
                >
            ` : `
                <span class="todo-title">${escapeHtml(todo.title)}</span>
            `}
        </div>
        <div class="todo-actions">
            ${isEditing ? `
                <button class="btn btn-secondary" onclick="saveEdit(${todo.id})">Save</button>
                <button class="btn btn-secondary" onclick="cancelEdit()">Cancel</button>
            ` : `
                <button class="btn btn-secondary" onclick="startEdit(${todo.id})">Edit</button>
                <button class="btn btn-danger" onclick="confirmDelete(${todo.id})">Delete</button>
            `}
        </div>
    `;
    
    return div;
}

// Update statistics
function updateStatistics() {
    const total = todos.length;
    const completed = todos.filter(todo => todo.completed).length;
    const pending = total - completed;
    
    totalCount.textContent = total;
    completedCount.textContent = completed;
    pendingCount.textContent = pending;
}

// Show toast notification
function showToast(message, type = 'success') {
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

/**
 * Event Handlers
 */

// Handle form submission
todoForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const title = todoInput.value.trim();
    if (!title) return;
    
    const success = await createTodo(title);
    if (success) {
        todoInput.value = '';
    }
});

// Toggle todo completion
async function toggleTodo(id) {
    const todo = todos.find(t => t.id === id);
    if (todo) {
        await updateTodo(id, { completed: !todo.completed });
    }
}

// Start editing a todo
function startEdit(id) {
    editingTodoId = id;
    renderTodos();
    
    // Focus the input
    const input = document.getElementById(`edit-input-${id}`);
    if (input) {
        input.focus();
        input.select();
    }
}

// Save edited todo
async function saveEdit(id) {
    const input = document.getElementById(`edit-input-${id}`);
    if (!input) return;
    
    const newTitle = input.value.trim();
    if (!newTitle) {
        showToast('Title cannot be empty', 'error');
        return;
    }
    
    const success = await updateTodo(id, { title: newTitle });
    if (success) {
        editingTodoId = null;
        renderTodos();
    }
}

// Cancel editing
function cancelEdit() {
    editingTodoId = null;
    renderTodos();
}

// Confirm and delete todo
function confirmDelete(id) {
    const todo = todos.find(t => t.id === id);
    if (!todo) return;
    
    if (confirm(`Are you sure you want to delete "${todo.title}"?`)) {
        deleteTodo(id);
    }
}

/**
 * Utility Functions
 */

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Handle Enter key in edit mode
document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && editingTodoId !== null) {
        saveEdit(editingTodoId);
    } else if (e.key === 'Escape' && editingTodoId !== null) {
        cancelEdit();
    }
});

/**
 * Initialize Application
 */
document.addEventListener('DOMContentLoaded', () => {
    fetchTodos();
});

// Made with Bob
