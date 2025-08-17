import os
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import openai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configure OpenAI
openai.api_key = os.environ.get('OPENAI_API_KEY')

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/health')
def health():
    """Health check endpoint"""
    try:
        # Test if OpenAI API key is configured
        if not openai.api_key:
            return jsonify({
                'status': 'error',
                'message': 'OpenAI API key not configured'
            }), 500
        
        return jsonify({
            'status': 'healthy',
            'message': 'AI Agent backend is running',
            'openai_configured': bool(openai.api_key)
        })
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat endpoint with OpenAI integration"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        user_message = data['message']
        logger.info(f"Received chat message: {user_message}")
        
        # Check if OpenAI API key is configured
        if not openai.api_key:
            logger.error("OpenAI API key not configured")
            return jsonify({'error': 'OpenAI API key not configured'}), 500
        
        # Create OpenAI client
        client = openai.OpenAI(api_key=openai.api_key)
        
        # Make API call to OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a helpful AI assistant specializing in real estate. Provide professional, informative responses about real estate topics, property investment, market analysis, and related services."
                },
                {
                    "role": "user", 
                    "content": user_message
                }
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        logger.info("OpenAI response received successfully")
        
        return jsonify({
            'response': ai_response,
            'status': 'success'
        })
        
    except openai.AuthenticationError as e:
        logger.error(f"OpenAI Authentication Error: {str(e)}")
        return jsonify({
            'error': 'OpenAI API authentication failed. Please check your API key.',
            'details': str(e)
        }), 401
        
    except openai.RateLimitError as e:
        logger.error(f"OpenAI Rate Limit Error: {str(e)}")
        return jsonify({
            'error': 'OpenAI rate limit exceeded. Please try again later.',
            'details': str(e)
        }), 429
        
    except openai.APIError as e:
        logger.error(f"OpenAI API Error: {str(e)}")
        return jsonify({
            'error': 'OpenAI API error occurred.',
            'details': str(e)
        }), 500
        
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {str(e)}")
        return jsonify({
            'error': 'An unexpected error occurred.',
            'details': str(e)
        }), 500

@app.route('/api/organize-task', methods=['POST'])
def organize_task():
    """Task organization endpoint"""
    try:
        data = request.get_json()
        if not data or 'task' not in data:
            return jsonify({'error': 'Task description is required'}), 400
        
        task = data['task']
        logger.info(f"Organizing task: {task}")
        
        if not openai.api_key:
            return jsonify({'error': 'OpenAI API key not configured'}), 500
        
        client = openai.OpenAI(api_key=openai.api_key)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional task organizer. Break down complex tasks into clear, actionable steps with time estimates. Format your response as a numbered list with brief descriptions and estimated time for each step."
                },
                {
                    "role": "user",
                    "content": f"Please organize this task into actionable steps: {task}"
                }
            ],
            max_tokens=600,
            temperature=0.5
        )
        
        organization = response.choices[0].message.content
        
        return jsonify({
            'organization': organization,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error in organize-task endpoint: {str(e)}")
        return jsonify({
            'error': 'Failed to organize task.',
            'details': str(e)
        }), 500

@app.route('/api/schedule-meeting', methods=['POST'])
def schedule_meeting():
    """Meeting scheduling endpoint"""
    try:
        data = request.get_json()
        if not data or 'meeting' not in data:
            return jsonify({'error': 'Meeting details are required'}), 400
        
        meeting = data['meeting']
        logger.info(f"Scheduling meeting: {meeting}")
        
        if not openai.api_key:
            return jsonify({'error': 'OpenAI API key not configured'}), 500
        
        client = openai.OpenAI(api_key=openai.api_key)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional meeting planner. Create detailed meeting agendas with time allocations, preparation requirements, and key discussion points. Format your response clearly with sections for agenda, preparation, and expected outcomes."
                },
                {
                    "role": "user",
                    "content": f"Please create a meeting plan for: {meeting}"
                }
            ],
            max_tokens=600,
            temperature=0.5
        )
        
        schedule = response.choices[0].message.content
        
        return jsonify({
            'schedule': schedule,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error in schedule-meeting endpoint: {str(e)}")
        return jsonify({
            'error': 'Failed to schedule meeting.',
            'details': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
