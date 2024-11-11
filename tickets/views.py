# tickets/views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
import google.auth
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import requests
import base64
from openai import OpenAI




def bot_response(request):
    # Aquí puedes personalizar la lógica de tu bot
    response_data = {
        'message': '¡Hola! Soy el bot de soporte. ¿En qué puedo ayudarte hoy?'
    }
    return JsonResponse(response_data)

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from utils.email_service import GmailService

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@require_http_methods(["GET"])
def get_emails(request):
    try:
        max_results = int(request.GET.get('max_results', 10))
        gmail_service = GmailService()
        gmail_service.authenticate()
        emails = gmail_service.get_emails(max_results=max_results)
        
        return JsonResponse({
            'status': 'success',
            'data': emails
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_email_detail(request, email_id):
    try:
        gmail_service = GmailService()
        gmail_service.authenticate()
        
        # Obtener los detalles del correo usando el método get_email_details
        email_detail = gmail_service.get_email_details(email_id)
        
        if email_detail is None:
            return JsonResponse({
                'status': 'error',
                'message': 'No se pudo obtener los detalles del correo'
            }, status=404)
        
        return JsonResponse({
            'status': 'success',
            'data': email_detail
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
    

@csrf_exempt
@require_http_methods(["GET"])
def get_emails_with_attachments(request):
    try:
        gmail_service = GmailService()
        gmail_service.authenticate()
        
        max_results = request.GET.get('max_results', 10)
        emails_with_attachments = gmail_service.get_emails_with_attachments(max_results=int(max_results))
        
        return JsonResponse({
            'status': 'success',
            'data': emails_with_attachments
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
    
# Add llama_index import
from llama_index import Document, GPTSimpleVectorIndex

@csrf_exempt
def gmail_notification(request):
    if request.method == 'GET':
        try:
            # Initializing Gmail Service
            gmail_service = GmailService()
            gmail_service.authenticate()

            max_results = request.GET.get('max_results', 10)
            emails_with_attachments = gmail_service.get_emails_with_attachments(max_results=int(max_results))

            # Initialize LlamaIndex (assume index.json is your knowledge base)
            index = GPTSimpleVectorIndex.load_from_disk("index.json")

            nvidia_response = []
            email_data = emails_with_attachments

            # Loop through each email for processing
            for email in email_data:
                email_id = email.get('id')
                subject = email.get('subject', 'Sin asunto')
                snippet = email.get('snippet', 'Sin contenido')
                base64_image = gmail_service.download_attachment(email_id)

                # Use LlamaIndex to retrieve context based on the email snippet
                context = index.query(snippet)

                # Prepare prompt with additional context from LlamaIndex
                promt_it = f"""
                    Using the following information as context, please respond to the client inquiry.

                    Context: {context}

                    Actúa como un agente de soporte técnico... (Your existing prompt text here)
                    
                    Asunto: {subject} - {snippet}
                """

                # Format the messages to send to Mistral API
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": promt_it},
                            {"type": "image_url", "image_url": f"data:image/jpeg;base64,{base64_image}" if base64_image else ""}
                        ]
                    }
                ]

                # Mistral API request setup (as in your original code)
                mistral_url = "https://api.mistral.ai/v1/chat/completions"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {os.getenv('MISTRAL_API_KEY')}"
                }
                data = {
                    "model": 'pixtral-12b-2409',
                    "messages": messages,
                    "max_tokens": 2000
                }

                response = requests.post(mistral_url, headers=headers, json=data)

                if response.status_code == 200:
                    chat_response = response.json()
                    mistral_text = chat_response['choices'][0]['message']['content']
                else:
                    mistral_text = "Error en la respuesta de Mistral"
                
                # NVIDIA API call with the enhanced response
                client = OpenAI(
                    base_url="https://integrate.api.nvidia.com/v1",
                    api_key=os.getenv("KEY_NVIDIA")
                )

                completion = client.chat.completions.create(
                    model="nvidia/llama-3.1-nemotron-70b-instruct",
                    messages=[
                        {
                            "role": "user",
                            "content": f"{mistral_text} -- Please validate the above information to ensure accuracy and provide the finalized content."
                        }
                    ],
                    temperature=0.5,
                    top_p=1,
                    max_tokens=1024,
                    stream=False
                )

                nvidia_content = "".join([chunk.choices[0].delta.content for chunk in completion])

                # Append the NVIDIA response to your response data
                nvidia_response.append({
                    "subject": subject,
                    "snippet": snippet,
                    "mistral_response": mistral_text,
                    "nvidia_response": nvidia_content,
                    "id": email_id
                })

            return JsonResponse({
                'status': 'success',
                'data': nvidia_response
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)