import os
from bs4 import BeautifulSoup
import requests
from requests.auth import HTTPBasicAuth
from PIL import Image
from io import BytesIO
import pandas as pd
from urllib.parse import urlparse
import os
import cv2
import numpy as np
import pytesseract
import subprocess
from PIL import Image
from pypdf import PdfReader
from ai71 import AI71
import os
import PyPDF2
import pandas as pd
def extract_text_from_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Image not found or unable to load")

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)
    
    return text
from inference_sdk import InferenceHTTPClient
import base64
UPLOAD_FOLDER = '/code/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

pdf_text=''
AI71_API_KEY = os.environ.get('AI71_API_KEY')
def generate_response(query,chat_history):
    response = ''
    for chunk in AI71(AI71_API_KEY).chat.completions.create(
            model="tiiuae/falcon-180b-chat",
            messages=[
                {"role": "system", "content": "You are a best agricultural assistant.Remember to give response not more than 2 sentence.Greet the user if user greets you."},
                {"role": "user",
                 "content": f'''Answer the query based on history {chat_history}:{query}'''},
            ],
            stream=True,
    ):
        if chunk.choices[0].delta.content:
            response += chunk.choices[0].delta.content
    return response.replace("###", '').replace('\nUser:','')
class ConversationBufferMemory:
    def __init__(self, max_size):
        self.memory = []
        self.max_size = max_size

    def add_to_memory(self, interaction):
        self.memory.append(interaction)
        if len(self.memory) > self.max_size:
            self.memory.pop(0)  # Remove the oldest interaction

    def get_memory(self):
        return self.memory
def predict_pest(filepath):
    try:
        CLIENT = InferenceHTTPClient(
            api_url="https://detect.roboflow.com",
            api_key="oF1aC4b1FBCDtK8CoKx7"
        )
        result = CLIENT.infer(filepath, model_id="pest-detection-ueoco/1")
        a= result['predictions'][0]
        if a=='x':
            return 'APHIDS'
        return a
    except:
        return None
    

def predict_disease(filepath):
    try:
        CLIENT = InferenceHTTPClient(
        api_url="https://classify.roboflow.com",
        api_key="oF1aC4b1FBCDtK8CoKx7"
    )
        result = CLIENT.infer(filepath, model_id="plant-disease-detection-iefbi/1")
        a= result['predicted_classes'][0]
        if a=='x':
            return 'APHIDS'
        return a
    except:
        return None


def convert_img(url, account_sid, auth_token):
    if 1==1:
        # Make the request to the media URL with authentication
        response = requests.get(url.replace(' ',''), auth=HTTPBasicAuth(account_sid, auth_token))
        response.raise_for_status()  # Raise an error for bad responses

        # Determine a filename from the URL
        parsed_url = urlparse(url.replace(' ',''))
        media_id = parsed_url.path.split('/')[-1]  # Get the last part of the URL path
        filename = f"image.jpg"

        # Save the media content to a .txt file
        txt_filepath = os.path.join(UPLOAD_FOLDER, filename)
        with open(txt_filepath, 'wb') as file:
            file.write(response.content)
        
        print(f"Media downloaded successfully and saved as {txt_filepath}")
        return txt_filepath

    else :
        return 'errir in process none'

def get_weather(city):
  city=city.strip()
  city=city.replace(' ',"+")
  r = requests.get(f'https://www.google.com/search?q=weather+in+{city}')

  soup=BeautifulSoup(r.text,'html.parser')
  temp = soup.find('div', class_='BNeawe iBp4i AP7Wnd').text
  
  return (temp)


from zenrows import ZenRowsClient
from bs4 import BeautifulSoup
Zenrow_api=os.environ.get('Zenrow_api')
# Initialize ZenRows client with your API key
client = ZenRowsClient(str(Zenrow_api))

def get_rates():    # URL to scrape
    url = "https://www.kisandeals.com/mandiprices/ALL/TAMIL-NADU/ALL"

    # Fetch the webpage content using ZenRows
    response = client.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the raw HTML content with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the table rows containing the data
        rows = soup.select('table tbody tr')
        data = {}
        for row in rows:
            # Extract commodity and price using BeautifulSoup
            columns = row.find_all('td')
            if len(columns) >= 2:
                commodity = columns[0].get_text(strip=True)
                price = columns[1].get_text(strip=True)
                if '₹' in price:
                    data[commodity] = price
    return str(data)+" This are the prices for 1 kg"




def get_news(): 
    news=[]   # URL to scrape
    url = "https://economictimes.indiatimes.com/news/economy/agriculture?from=mdr"

    # Fetch the webpage content using ZenRows
    response = client.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the raw HTML content with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the table rows containing the data
        headlines = soup.find_all("div", class_="eachStory")
        for story in headlines:
    # Extract the headline
            headline = story.find('h3').text.strip()
            news.append(headline)
    return news



def download_and_save_as_txt(url, account_sid, auth_token):
    global pdf_text
    try:
        # Make the request to the media URL with authentication
        response = requests.get(url, auth=HTTPBasicAuth(account_sid, auth_token))
        response.raise_for_status()  # Raise an error for bad responses

        # Determine a filename from the URL
        parsed_url = urlparse(url)
        media_id = parsed_url.path.split('/')[-1]  # Get the last part of the URL path
        filename = f"pdf_file.pdf"

        # Save the media content to a .txt file
        txt_filepath = os.path.join(UPLOAD_FOLDER, filename)
        with open(txt_filepath, 'wb') as file:
            file.write(response.content)
        
        print(f"Media downloaded successfully and saved as {txt_filepath}")
        pdf_text=extract_text_from_pdf(txt_filepath)
        return txt_filepath

    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except Exception as err:
        print(f"An error occurred: {err}")


def extract_text_from_pdf(pdf_path):
    global pdf_text
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        pdf_text = ''
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            pdf_text += page.extract_text()
        return pdf_text


def respond_pdf(query):
    extracted_text=pdf_text
    res = ''
    for chunk in AI71(AI71_API_KEY).chat.completions.create(
        model="tiiuae/falcon-11b",
        messages=[
            {"role": "system", "content": "You are a  pdf answering assistant and you have a pdf as a data."},
            {"role": "user", "content": f"Content:{extracted_text},Query:{query}"},
        ],
        stream=True,
    ):
        if chunk.choices[0].delta.content:
            res += chunk.choices[0].delta.content
    return ( res.replace("User:",'').strip())


def booktask(data):
    res = ''
    for chunk in AI71(AI71_API_KEY).chat.completions.create(
        model="tiiuae/falcon-11b",
        messages=[
            {"role": "system", "content": "You are an assistant."},
            {"role": "user", "content": f"My bookkeeping data is {data}.Provide the data in points."},
        ],
        stream=True,
    ):
        if chunk.choices[0].delta.content:
            res += chunk.choices[0].delta.content
    return ( res.replace("User:",'').strip())



def return_bookdata(querry,data):
    res = ''
    for chunk in AI71(AI71_API_KEY).chat.completions.create(
        model="tiiuae/falcon-11b",
        messages=[
            {"role": "system", "content": "You are an assistant."},
            {"role": "user", "content": f"My notes data is {data}.user:{querry.replace('bookkeeping','data')}.Give the format of bookkeeping data in points.Make your response very concise to maximum of 10 points"},
        ],
        stream=True,
    ):
        if chunk.choices[0].delta.content:
            res += chunk.choices[0].delta.content
    return ( res.replace("User:",'').strip())