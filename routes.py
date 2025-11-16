from flask import session, request, jsonify, render_template
from app import app
from flask_login import login_required, current_user
from chat_service import chat_service
from db_service import (
    save_chat_history, get_chat_history, get_db,
    create_conversation, get_conversations, get_conversation,
    add_message_to_conversation, update_conversation_title, delete_conversation
)
import asyncio


# Make session permanent
@app.before_request
def make_session_permanent():
    session.permanent = True

# Serve React app for all frontend routes
@app.route('/')
@app.route('/<path:path>')
def serve_react(path=''):
    if path.startswith('api/') or path.startswith('auth/') or path.startswith('login/'):
        return jsonify({'error': 'Not found'}), 404
    
    try:
        return app.send_static_file('index.html')
    except:
        return jsonify({'error': 'Frontend not built. Run: cd client && npm run build'}), 500

# API: Get current user info
@app.route('/api/user')
def get_user():
    if current_user.is_authenticated:
        return jsonify({
            'id': current_user.id,
            'email': current_user.email,
            'first_name': current_user.first_name,
            'last_name': current_user.last_name,
            'profile_image_url': current_user.profile_image_url
        })
    return jsonify({'error': 'Not authenticated'}), 401

# API: Chat endpoint with RAG and conversation support
@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message')
        conversation_id = data.get('conversation_id')
        personality = data.get('personality', 'neutral')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Validate personality
        valid_personalities = ['neutral', 'ronaldo', 'messi', 'manutd']
        if personality not in valid_personalities:
            personality = 'neutral'
        
        # Check if user is logged in
        is_logged_in = current_user.is_authenticated
        
        # Get conversation history if conversation_id is provided AND user is logged in
        conversation_history = []
        if is_logged_in and conversation_id:
            conv = get_conversation(conversation_id, user_id=current_user.id)
            if conv:
                conversation_history = conv.get('messages', [])
            else:
                return jsonify({'error': 'Conversation not found'}), 404
        elif is_logged_in and not conversation_id:
            # Create new conversation if user is logged in but no conversation_id
            conversation_id = create_conversation(current_user.id, title="New Chat")
        
        # Get AI reply with conversation context and personality
        reply = asyncio.run(chat_service.chat(message, conversation_history, personality))
        
        # Save messages to conversation ONLY if user is logged in
        if is_logged_in and conversation_id:
            if not add_message_to_conversation(conversation_id, 'user', message, user_id=current_user.id):
                return jsonify({'error': 'Failed to save message'}), 500
            if not add_message_to_conversation(conversation_id, 'assistant', reply, user_id=current_user.id):
                return jsonify({'error': 'Failed to save reply'}), 500
            
            # Auto-generate title from first message if it's a new conversation
            if len(conversation_history) == 0 and message:
                # Use first 50 chars of message as title
                title = message[:50] + ('...' if len(message) > 50 else '')
                update_conversation_title(conversation_id, title, user_id=current_user.id)
        
        return jsonify({
            'reply': reply,
            'conversation_id': conversation_id if is_logged_in else None,
            'guest_mode': not is_logged_in
        })
        
    except Exception as error:
        print(f'Chat error: {str(error)}')
        return jsonify({'error': str(error)}), 500

# API: Get all conversations
@app.route('/api/conversations', methods=['GET'])
@login_required
def get_conversations_route():
    try:
        conversations = get_conversations(user_id=current_user.id, limit=50)
        return jsonify(conversations)
    except Exception as error:
        return jsonify({'error': str(error)}), 500

# API: Get a specific conversation
@app.route('/api/conversations/<conversation_id>', methods=['GET'])
@login_required
def get_conversation_route(conversation_id):
    try:
        conv = get_conversation(conversation_id, user_id=current_user.id)
        if not conv:
            return jsonify({'error': 'Conversation not found'}), 404
        return jsonify(conv)
    except Exception as error:
        return jsonify({'error': str(error)}), 500

# API: Create new conversation
@app.route('/api/conversations', methods=['POST'])
@login_required
def create_conversation_route():
    try:
        data = request.get_json() or {}
        title = data.get('title', 'New Chat')
        conversation_id = create_conversation(current_user.id, title)
        return jsonify({'id': conversation_id, 'title': title})
    except Exception as error:
        return jsonify({'error': str(error)}), 500

# API: Delete conversation
@app.route('/api/conversations/<conversation_id>', methods=['DELETE'])
@login_required
def delete_conversation_route(conversation_id):
    try:
        if not delete_conversation(conversation_id, user_id=current_user.id):
            return jsonify({'error': 'Conversation not found or access denied'}), 404
        return jsonify({'success': True})
    except Exception as error:
        return jsonify({'error': str(error)}), 500

# API: Get chat history (legacy endpoint)
@app.route('/api/chat/history', methods=['GET'])
@login_required
def get_chat_history_route():
    try:
        histories = get_chat_history(user_id=current_user.id, limit=50)
        return jsonify(histories)
    except Exception as error:
        return jsonify({'error': str(error)}), 500