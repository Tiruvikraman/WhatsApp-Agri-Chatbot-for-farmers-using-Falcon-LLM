from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import os 
import shutil
from other_function import ConversationBufferMemory,generate_response,get_weather,get_rates,get_news,convert_img,predict_disease,predict_pest, download_and_save_as_txt,respond_pdf,extract_text_from_image,booktask,return_bookdata
from bs4 import BeautifulSoup
import requests
from requests.auth import HTTPBasicAuth
from PIL import Image
from io import BytesIO
import pandas as pd
from urllib.parse import urlparse
from pypdf import PdfReader
from ai71 import AI71
import uuid
from inference_sdk import InferenceHTTPClient
import base64

app = Flask(__name__)
UPLOAD_FOLDER = '/code/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
bookdata=''
conversation_memory = ConversationBufferMemory(max_size=0)

account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
client = Client(account_sid, auth_token)
from_whatsapp_number = 'whatsapp:+14155238886'

PROMPT_TEMPLATE = """
Answer the question based only on the following context:
{context}
---
Answer the question based on the above context: {question}
"""



@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    global bookdata
    incoming_msg = request.values.get('Body', '').lower()
    sender = request.values.get('From')
    num_media = int(request.values.get('NumMedia', 0))

    chat_history = conversation_memory.get_memory()

    if num_media > 0:
        media_url = request.values.get('MediaUrl0')
        content_type = request.values.get('MediaContentType0')

        if content_type.startswith('image/'):
            # Handle image processing (disease/pest detection)
            if 1==1:
                filepath = convert_img(media_url, account_sid, auth_token)
            
            bd=extract_text_from_image(filepath)
            if bd!='':
                bookdata=booktask(bd)
                response_text="Your report for bookkeeping saved successfully."
            elif 'none' not in filepath:
                if  predict_pest(filepath):
                    res=predict_pest(filepath)
                    if  res=='x' or  res=='X':
                                   response_text     ='APHIDS'
                    else:
                        response_text = predict_pest(filepath)
                    
                
                elif predict_disease(filepath):
                    res=predict_disease(filepath)
                    if  res=='x' or  res=='X':
                                   response_text     ='APHIDS'
                    else:
                        response_text = predict_disease(filepath)
                
                else:
                    response_text = "Please upload other image with good quality."
            else:
                response_text = 'no data'

        else:
            # Handle PDF processing
            filepath = download_and_save_as_txt(media_url, account_sid, auth_token)
            response_text = 'PDF uploaded successfully'
    elif ('weather' in incoming_msg.lower()) or ('climate' in incoming_msg.lower()) or (
            'temperature' in incoming_msg.lower()):
        
        weather = get_weather(incoming_msg.lower())
        response_text = generate_response(incoming_msg + ' data is ' + weather+"convert to celcius.Make sure you return only answer.", chat_history)
    elif 'bookkeeping' in incoming_msg:
        response_text = '''1. General Information Farmer: John Doe | Farm: Green Valley Farms | Size: 50 acres Location: XYZ Village, State, Country | Period: Jan 1, 2024 - Dec 31, 2024 \n2. Income Crop Sales (Wheat): $2,000 | Livestock Sales (Cattle): $7,500 Subsidies: $1,000 | Equipment Rental: $500 \n3. Expenses & Assets Expenses: Seeds/Fertilizers: $1,000 | Labor: $2,000 | Maintenance: $300 | Fuel: $600 | Feed: $2,000 | Insurance: $800 | Utilities: $400 Assets: Tractor: $25,000 (Depreciation: $2,500) | Land: $100,000 (Market Value: $120,000) | Cattle: 50 head (Value: $75,000)'''
    elif ('rates' in incoming_msg.lower()) or ('price' in incoming_msg.lower()) or (
            'market' in incoming_msg.lower()) or ('rate' in incoming_msg.lower()) or ('prices' in incoming_msg.lower()):
        rates = get_rates()
        response_text = generate_response(incoming_msg + ' data is ' + rates, chat_history)
    elif ('news' in incoming_msg.lower()) or ('information' in incoming_msg.lower()):
        news = get_news()
        response_text = generate_response('Summarise and provide the top 5 news in india as bullet points' + ' Data is ' + str(news), chat_history)
    elif ('pdf' in incoming_msg.lower()):
        response_text =respond_pdf(incoming_msg)
    elif ('farm data' in incoming_msg.lower()):
        response_text =' Click the link to monitor your farm.\n https://huggingface.co/spaces/Neurolingua/Smart-Agri-system'
    else:
        response_text = generate_response(incoming_msg, chat_history)

    send_message(sender, response_text)
    return '', 204



def process_and_query_pdf(filepath):
    # Read and process the PDF
    reader = PdfReader(filepath)
    text = ''
    for page in reader.pages:
        text += page.extract_text()

    if not text:
        return "Sorry, the PDF content could not be extracted."
    
    # Generate response based on extracted PDF content
    response_text = generate_response(f"The PDF content is {text}", "")
    return response_text

def send_message(recipient, message):
    client.messages.create(
        body=message,
        from_=from_whatsapp_number,
        to=recipient
    )
def send_initial_message(to_number):
    send_message(
        f'whatsapp:{to_number}',
        'Welcome to the Agri AI Chatbot! How can I assist you today? You may get real-time information from me!!'
    )
if __name__ == "__main__":
    send_initial_message('919080522395') 
    send_initial_message('916382792828')
    app.run(host='0.0.0.0', port=7860,debug=1==1)