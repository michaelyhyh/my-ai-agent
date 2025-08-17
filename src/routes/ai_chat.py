from flask import Blueprint, request, jsonify
import openai
import os
from datetime import datetime
import json

ai_chat_bp = Blueprint('ai_chat', __name__)

# Initialize OpenAI client
openai.api_key = os.getenv('OPENAI_API_KEY')

# System prompt for the AI agent
SYSTEM_PROMPT = """You are an intelligent AI assistant specialized in real estate and work organization. Your capabilities include:

1. REAL ESTATE EXPERTISE:
- Help clients find properties based on their preferences
- Provide market insights and property recommendations
- Schedule property viewings and meetings with agents
- Answer questions about buying, selling, and renting

2. WORK ORGANIZATION:
- Create and manage task lists
- Schedule meetings and appointments
- Set reminders and deadlines
- Organize projects and workflows
- Provide productivity tips and strategies

3. GENERAL ASSISTANCE:
- Answer questions intelligently
- Provide helpful information and advice
- Maintain context throughout conversations
- Be professional, friendly, and efficient

Always be helpful, accurate, and maintain a professional tone. When organizing work, be specific about dates, times, and actionable steps. For real estate inquiries, ask relevant questions to better understand client needs.

Current date and time: {current_time}
"""

@ai_chat_bp.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        conversation_history = data.get('history', [])
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Prepare conversation for OpenAI
        messages = [
            {
                "role": "system", 
                "content": SYSTEM_PROMPT.format(current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            }
        ]
        
        # Add conversation history
        for msg in conversation_history[-10:]:  # Keep last 10 messages for context
            messages.append({
                "role": msg.get('role', 'user'),
                "content": msg.get('content', '')
            })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        return jsonify({
            'response': ai_response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': 'Failed to process message'}), 500

@ai_chat_bp.route('/api/organize-task', methods=['POST'])
def organize_task():
    try:
        data = request.get_json()
        task_description = data.get('task', '')
        
        if not task_description:
            return jsonify({'error': 'Task description is required'}), 400
        
        # Use AI to organize the task
        messages = [
            {
                "role": "system",
                "content": """You are a work organization expert. When given a task description, break it down into:
1. Clear, actionable steps
2. Estimated time for each step
3. Priority level (High/Medium/Low)
4. Suggested deadline
5. Required resources or tools

Format your response as a structured JSON object with these fields:
- title: Clear task title
- steps: Array of step objects with {step, time_estimate, notes}
- priority: High/Medium/Low
- estimated_total_time: Total time needed
- suggested_deadline: Suggested completion date
- resources_needed: Array of required resources
- tips: Array of helpful tips for completion

Current date: {current_date}
""".format(current_date=datetime.now().strftime("%Y-%m-%d"))
            },
            {
                "role": "user",
                "content": f"Please organize this task: {task_description}"
            }
        ]
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=800,
            temperature=0.3
        )
        
        ai_response = response.choices[0].message.content
        
        # Try to parse as JSON, fallback to text if needed
        try:
            organized_task = json.loads(ai_response)
        except:
            organized_task = {
                "title": "Task Organization",
                "description": ai_response,
                "timestamp": datetime.now().isoformat()
            }
        
        return jsonify(organized_task)
        
    except Exception as e:
        print(f"Error in organize-task endpoint: {str(e)}")
        return jsonify({'error': 'Failed to organize task'}), 500

@ai_chat_bp.route('/api/schedule-meeting', methods=['POST'])
def schedule_meeting():
    try:
        data = request.get_json()
        meeting_details = data.get('details', '')
        
        if not meeting_details:
            return jsonify({'error': 'Meeting details are required'}), 400
        
        # Use AI to help schedule the meeting
        messages = [
            {
                "role": "system",
                "content": """You are a scheduling assistant. When given meeting details, help organize the meeting by providing:
1. Suggested meeting agenda
2. Recommended duration
3. Preparation checklist
4. Follow-up actions
5. Meeting best practices

Format as JSON with fields: title, agenda, duration, preparation, follow_up, tips
Current date and time: {current_time}
""".format(current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            },
            {
                "role": "user",
                "content": f"Help me organize this meeting: {meeting_details}"
            }
        ]
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=600,
            temperature=0.3
        )
        
        ai_response = response.choices[0].message.content
        
        try:
            meeting_plan = json.loads(ai_response)
        except:
            meeting_plan = {
                "title": "Meeting Organization",
                "details": ai_response,
                "timestamp": datetime.now().isoformat()
            }
        
        return jsonify(meeting_plan)
        
    except Exception as e:
        print(f"Error in schedule-meeting endpoint: {str(e)}")
        return jsonify({'error': 'Failed to organize meeting'}), 500

