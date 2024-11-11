Table of Contents
Overview
Features
Prerequisites
Installation
Configuration
API Documentation
Usage
Development
Contributing
Overview
This Django-based system provides an intelligent email support solution by integrating Gmail API with advanced AI models (Mistral and NVIDIA) to automate support responses.
Features
Email Integration
- Gmail API integration
- Automatic email fetching
- Attachment handling
- Email detail retrieval
AI Capabilities
- Mistral AI integration
- NVIDIA LLM integration
- Context-aware responses using LlamaIndex
- Image processing support
API Endpoints
- RESTful architecture
- Comprehensive error handling
- CSRF-exempt endpoints
- Pagination support
Prerequisites
- Python
- Django
- Google Cloud Platform account
- Mistral AI API key
- NVIDIA API key
Installation
Clone Repository
```bash
git clone <repository-url>
cd <project-directory>
```
Virtual Environment Setup
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```
Install Dependencies
```bash
pip install -r requirements.txt
```
Environment Configuration
```bash
# Create .env file with:
MISTRAL_API_KEY=your_mistral_api_key
KEY_NVIDIA=your_nvidia_api_key
```
Configuration
Google OAuth Setup
1. Create project in Google Cloud Console
2. Enable Gmail API
3. Configure OAuth consent screen
4. Download credentials.json
5. Place in project root
LlamaIndex Setup
1. Prepare knowledge base
2. Generate index.json
3. Place in appropriate directory
API Documentation
Email Endpoints
Get Emails
```markdown
GET /emails/
Query Parameters:
- max_results: int (default: 10)
```
Get Email Details
```markdown
GET /emails/<email_id>/
```
Get Emails with Attachments
```markdown
GET /emails/attachments/
Query Parameters:
- max_results: int (default: 10)
```
Process Emails with AI
```markdown
GET /gmail-notification/
Query Parameters:
- max_results: int (default: 10)
```
Response Format
```json
{
    "status": "success|error",
    "data": [...],
    "message": "error_message"
}
```
Usage
Starting the Server
```bash
python manage.py runserver
```
API Examples
```bash
# Get emails
curl http://localhost:8000/emails/?max_results=10

# Get AI responses
curl http://localhost:8000/gmail-notification/
```
Development
Project Structure
```markdown
project/
├── tickets/
│   ├── views.py
│   ├── urls.py
│   └── models.py
├── utils/
│   └── email_service.py
├── requirements.txt
└── manage.py
```
Key Components
Email Service
```python
class GmailService:
    def authenticate(self)
    def get_emails(self, max_results)
    def get_email_details(self, email_id)
    def get_emails_with_attachments(self, max_results)
```
AI Integration
```python
# Mistral AI
- API endpoint: https://api.mistral.ai/v1/chat/completions
- Model: pixtral-12b-2409

# NVIDIA
- API endpoint: https://integrate.api.nvidia.com/v1
- Model: nvidia/llama-3.1-nemotron-70b-instruct

License
[Add License Information]
Support
[Add Support Information]
Note
Keep all credentials secure and monitor API usage regularly.
For more information, contact [Your Contact Information].
