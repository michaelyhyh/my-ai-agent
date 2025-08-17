import os
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import openai

# Initialize Flask app
app = Flask(__name__, static_folder='static')
CORS(app)

# Configure OpenAI
openai.api_key = os.environ.get('OPENAI_API_KEY')

@app.route('/')
def index():
    """Serve the main page"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory(app.static_folder, filename)

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle AI chat requests"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        message = data.get('message', '')
        history = data.get('history', [])
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Check if OpenAI API key is configured
        if not openai.api_key:
            return jsonify({'error': 'OpenAI API key not configured'}), 500
        
        # Prepare messages for OpenAI
        messages = [
            {
                "role": "system", 
                "content": "You are an intelligent AI assistant specializing in real estate. You help with property searches, market analysis, investment advice, and general real estate questions. Be helpful, professional, and provide detailed responses."
            }
        ]
        
        # Add conversation history
        for msg in history[-10:]:  # Keep last 10 messages
            messages.append(msg)
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        # Call OpenAI API
        client = openai.OpenAI(api_key=openai.api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        return jsonify({
            'response': ai_response,
            'status': 'success'
        })
        
    except openai.AuthenticationError:
        return jsonify({'error': 'Invalid OpenAI API key'}), 401
    except openai.RateLimitError:
        return jsonify({'error': 'OpenAI rate limit exceeded'}), 429
    except openai.APIError as e:
        return jsonify({'error': f'OpenAI API error: {str(e)}'}), 500
    except Exception as e:
        print(f"Chat error: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/organize-task', methods=['POST'])
def organize_task():
    """Handle task organization requests"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        task = data.get('task', '')
        
        if not task:
            return jsonify({'error': 'No task provided'}), 400
        
        # Check if OpenAI API key is configured
        if not openai.api_key:
            return jsonify({'error': 'OpenAI API key not configured'}), 500
        
        # Prepare prompt for task organization
        prompt = f"""
        Please organize this task into actionable steps: "{task}"
        
        Provide a response in the following JSON format:
        {{
            "title": "Task Title",
            "steps": [
                "Step 1: Description",
                "Step 2: Description",
                "Step 3: Description"
            ],
            "priority": "High/Medium/Low",
            "estimated_total_time": "X hours",
            "description": "Brief overview of the task"
        }}
        
        Focus on real estate and business tasks. Be specific and actionable.
        """
        
        # Call OpenAI API
        client = openai.OpenAI(api_key=openai.api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a task organization expert. Always respond with valid JSON format."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.3
        )
        
        ai_response = response.choices[0].message.content
        
        # Try to parse JSON response
        try:
            task_data = json.loads(ai_response)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            task_data = {
                "title": "Task Organization",
                "steps": [
                    "Step 1: Break down the task into smaller components",
                    "Step 2: Prioritize each component",
                    "Step 3: Create timeline and deadlines",
                    "Step 4: Execute and monitor progress"
                ],
                "priority": "Medium",
                "estimated_total_time": "2-4 hours",
                "description": ai_response
            }
        
        return jsonify(task_data)
        
    except Exception as e:
        print(f"Task organization error: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/schedule-meeting', methods=['POST'])
def schedule_meeting():
    """Handle meeting scheduling requests"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        details = data.get('details', '')
        
        if not details:
            return jsonify({'error': 'No meeting details provided'}), 400
        
        # Check if OpenAI API key is configured
        if not openai.api_key:
            return jsonify({'error': 'OpenAI API key not configured'}), 500
        
        # Prepare prompt for meeting planning
        prompt = f"""
        Please help plan this meeting: "{details}"
        
        Provide a response in the following JSON format:
        {{
            "title": "Meeting Title",
            "agenda": [
                "Agenda item 1",
                "Agenda item 2",
                "Agenda item 3"
            ],
            "duration": "X minutes/hours",
            "preparation": [
                "Preparation item 1",
                "Preparation item 2"
            ],
            "details": "Additional meeting details and recommendations"
        }}
        
        Focus on real estate and business meetings. Be professional and thorough.
        """
        
        # Call OpenAI API
        client = openai.OpenAI(api_key=openai.api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a meeting planning expert. Always respond with valid JSON format."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.3
        )
        
        ai_response = response.choices[0].message.content
        
        # Try to parse JSON response
        try:
            meeting_data = json.loads(ai_response)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            meeting_data = {
                "title": "Meeting Planning",
                "agenda": [
                    "Welcome and introductions",
                    "Review objectives and goals",
                    "Discussion of key topics",
                    "Action items and next steps"
                ],
                "duration": "60 minutes",
                "preparation": [
                    "Review relevant documents",
                    "Prepare questions and talking points"
                ],
                "details": ai_response
            }
        
        return jsonify(meeting_data)
        
    except Exception as e:
        print(f"Meeting scheduling error: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'openai_configured': bool(openai.api_key)
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
