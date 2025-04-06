# assistant/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import json
import logging
import base64
from django.conf import settings
from PIL import Image
import io

logger = logging.getLogger(__name__)

@csrf_exempt
def chat(request):
    if request.method == 'POST':
        try:
            message = request.POST.get('message', '')
            image_file = request.FILES.get('image')
            
            if image_file:
                # Use Gemini for image processing since it has multimodal capabilities
                try:
                    # Read image data
                    image_data = image_file.read()
                    # Call Gemini API with the image
                    gemini_response = call_gemini_with_image(message, image_data)
                    answer = f"**Gemini Answer (with image analysis):**\n{gemini_response}"
                except Exception as e:
                    logger.error(f"Image processing error: {str(e)}")
                    return JsonResponse({'error': 'Failed to process image'}, status=400)
            else:
                # Text-only request, use both APIs
                # Call Groq API
                groq_response = call_groq(message)
                
                # Call Gemini API
                gemini_response = call_gemini(message)
                
                answer = f"**Groq Answer:**\n{groq_response}\n\n" \
                         f"**Gemini Answer:**\n{gemini_response}"
            
            return JsonResponse({'answer': answer})
        
        except Exception as e:
            logger.error(f"Chat error: {str(e)}")
            return JsonResponse({'error': 'An error occurred while processing your request'}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def call_groq(prompt):
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama3-70b-8192",
        "messages": [{
            "role": "user",
            "content": f"Explain this problem to a student in grades 6-12 with clear steps: {prompt}"
        }],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        response_data = response.json()
        
        if 'choices' in response_data and len(response_data['choices']) > 0:
            return response_data['choices'][0]['message']['content']
        else:
            logger.error(f"Unexpected Groq response: {response_data}")
            return "Sorry, I couldn't process that request. Please try again."
            
    except Exception as e:
        logger.error(f"Groq API error: {str(e)}")
        return "Groq service is currently unavailable."

def call_gemini(prompt):
    try:
        payload = {
            "contents": [{
                "parts": [{"text": f"Explain this to a middle/high school student: {prompt}"}]
            }],
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_ONLY_HIGH"
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 1024
            }
        }
        
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={settings.GEMINI_API_KEY}",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        response_data = response.json()
        
        if 'candidates' in response_data and len(response_data['candidates']) > 0:
            return response_data['candidates'][0]['content']['parts'][0]['text']
        else:
            logger.error(f"Unexpected Gemini response: {response_data}")
            return "Gemini couldn't generate a response right now."
            
    except Exception as e:
        logger.error(f"Gemini API error: {str(e)}")
        return "Gemini service is currently unavailable."

def call_gemini_with_image(prompt, image_data):
    try:
        # Convert image to base64
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        payload = {
            "contents": [{
                "parts": [
                    {"text": f"Analyze this image and explain it to a middle/high school student. Question/prompt: {prompt}"},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",  # Adjust based on your needs or detect from uploaded file
                            "data": base64_image
                        }
                    }
                ]
            }],
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_ONLY_HIGH"
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 1024
            }
        }
        
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={settings.GEMINI_API_KEY}",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        response_data = response.json()
        
        if 'candidates' in response_data and len(response_data['candidates']) > 0:
            return response_data['candidates'][0]['content']['parts'][0]['text']
        else:
            logger.error(f"Unexpected Gemini response: {response_data}")
            return "Gemini couldn't analyze the image right now."
            
    except Exception as e:
        logger.error(f"Gemini Vision API error: {str(e)}")
        return "Gemini Vision service is currently unavailable."