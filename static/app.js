// State management
let personas = [];
let currentPersonaId = null;
let isEditMode = false;
let editingPersonaId = null;

// DOM Elements
const personaList = document.getElementById('persona-list');
const chatInterface = document.getElementById('chat-interface');
const noPersonaSelected = document.getElementById('no-persona-selected');
const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const addPersonaBtn = document.getElementById('add-persona-btn');
const editPersonaBtn = document.getElementById('edit-persona-btn');
const deletePersonaBtn = document.getElementById('delete-persona-btn');
const personaModal = document.getElementById('persona-modal');
const personaForm = document.getElementById('persona-form');
const modalTitle = document.getElementById('modal-title');
const closeModal = document.querySelector('.close');
const cancelBtn = document.getElementById('cancel-btn');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadPersonas();
    setupEventListeners();
});

// Event Listeners
function setupEventListeners() {
    addPersonaBtn.addEventListener('click', () => openModal(false));
    editPersonaBtn.addEventListener('click', () => openModal(true));
    deletePersonaBtn.addEventListener('click', deleteCurrentPersona);
    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    closeModal.addEventListener('click', () => personaModal.style.display = 'none');
    cancelBtn.addEventListener('click', () => personaModal.style.display = 'none');
    personaForm.addEventListener('submit', handleFormSubmit);
    window.addEventListener('click', (e) => {
        if (e.target === personaModal) {
            personaModal.style.display = 'none';
        }
    });
}

// Load all personas from API
async function loadPersonas() {
    try {
        const response = await fetch('/personas');
        personas = await response.json();
        renderPersonaList();
    } catch (error) {
        console.error('Error loading personas:', error);
        alert('Failed to load personas. Please refresh the page.');
    }
}

// Render persona list in left panel
function renderPersonaList() {
    personaList.innerHTML = '';

    if (personas.length === 0) {
        personaList.innerHTML = '<div style="padding: 20px; text-align: center; color: #999;">No personas yet. Create one to get started!</div>';
        return;
    }

    personas.forEach(persona => {
        const personaItem = document.createElement('div');
        personaItem.className = 'persona-item';
        if (currentPersonaId === persona.id) {
            personaItem.classList.add('active');
        }

        const info = [];
        if (persona.location) info.push(persona.location);
        if (persona.annual_income) info.push(`$${parseFloat(persona.annual_income).toLocaleString()}/year`);

        personaItem.innerHTML = `
            <h3>${persona.name}</h3>
            <p>${info.join(' • ') || 'No additional info'}</p>
        `;

        personaItem.addEventListener('click', () => selectPersona(persona.id));
        personaList.appendChild(personaItem);
    });
}

// Select a persona and show chat interface
function selectPersona(personaId) {
    currentPersonaId = personaId;
    const persona = personas.find(p => p.id === personaId);

    if (!persona) return;

    // Update UI
    noPersonaSelected.style.display = 'none';
    chatInterface.style.display = 'flex';

    // Update chat header
    document.getElementById('chat-persona-name').textContent = persona.name;

    const info = [];
    if (persona.location) info.push(persona.location);
    if (persona.annual_income) info.push(`Annual Income: $${parseFloat(persona.annual_income).toLocaleString()}`);
    if (persona.extras) info.push(persona.extras);

    document.getElementById('chat-persona-info').textContent = info.join(' • ') || 'No additional information';

    // Clear chat messages
    chatMessages.innerHTML = '<div class="message ai">Hello! I\'m ready to chat. What would you like to discuss?</div>';

    // Update active state
    renderPersonaList();
}

// Send message to OpenAI via API
async function sendMessage() {
    if (!currentPersonaId) return;

    const message = chatInput.value.trim();
    if (!message) return;

    // Add user message to chat
    addMessageToChat('user', message);
    chatInput.value = '';

    // Show loading message
    const loadingMsg = addMessageToChat('loading', 'Thinking...');

    try {
        const response = await fetch(`/personas/${currentPersonaId}/prompt`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message })
        });

        const data = await response.json();

        // Remove loading message
        loadingMsg.remove();

        if (response.ok) {
            addMessageToChat('ai', data.ai_response);
        } else {
            addMessageToChat('ai', `Error: ${data.error || 'Failed to get response'}`);
        }
    } catch (error) {
        console.error('Error sending message:', error);
        loadingMsg.remove();
        addMessageToChat('ai', 'Sorry, something went wrong. Please try again.');
    }
}

// Add message to chat display
function addMessageToChat(type, text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = text;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return messageDiv;
}

// Open modal for create/edit
function openModal(editMode) {
    isEditMode = editMode;
    personaModal.style.display = 'block';

    if (editMode) {
        modalTitle.textContent = 'Edit Persona';
        const persona = personas.find(p => p.id === currentPersonaId);
        if (persona) {
            editingPersonaId = persona.id;
            document.getElementById('persona-name').value = persona.name;
            document.getElementById('persona-location').value = persona.location || '';
            document.getElementById('persona-income').value = persona.annual_income || '';
            document.getElementById('persona-extras').value = persona.extras || '';
        }
    } else {
        modalTitle.textContent = 'Create New Persona';
        personaForm.reset();
        editingPersonaId = null;
    }
}

// Handle form submission (create or update)
async function handleFormSubmit(e) {
    e.preventDefault();

    const formData = {
        name: document.getElementById('persona-name').value,
        location: document.getElementById('persona-location').value || null,
        annual_income: document.getElementById('persona-income').value || null,
        extras: document.getElementById('persona-extras').value || null
    };

    try {
        let response;
        if (isEditMode && editingPersonaId) {
            response = await fetch(`/personas/${editingPersonaId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
        } else {
            response = await fetch('/personas', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
        }

        if (response.ok) {
            const persona = await response.json();
            personaModal.style.display = 'none';
            await loadPersonas();

            if (!isEditMode) {
                selectPersona(persona.id);
            } else {
                selectPersona(currentPersonaId);
            }
        } else {
            const error = await response.json();
            alert(`Error: ${error.error || 'Failed to save persona'}`);
        }
    } catch (error) {
        console.error('Error saving persona:', error);
        alert('Failed to save persona. Please try again.');
    }
}

// Delete current persona
async function deleteCurrentPersona() {
    if (!currentPersonaId) return;

    const persona = personas.find(p => p.id === currentPersonaId);
    if (!confirm(`Are you sure you want to delete "${persona.name}"?`)) {
        return;
    }

    try {
        const response = await fetch(`/personas/${currentPersonaId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            currentPersonaId = null;
            noPersonaSelected.style.display = 'flex';
            chatInterface.style.display = 'none';
            await loadPersonas();
        } else {
            const error = await response.json();
            alert(`Error: ${error.error || 'Failed to delete persona'}`);
        }
    } catch (error) {
        console.error('Error deleting persona:', error);
        alert('Failed to delete persona. Please try again.');
    }
}
