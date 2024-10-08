import os
import re
from flask import Flask, render_template, request, jsonify
from bs4 import BeautifulSoup

app = Flask(__name__)

WEBPAGES_DIRECTORY = '../rec'  # Change this to your actual directory path

def search_webpages(search_term):
    results = []
    
    for filename in os.listdir(WEBPAGES_DIRECTORY):
        if filename.endswith('.html') or filename.endswith('.htm'):
            filepath = os.path.join(WEBPAGES_DIRECTORY, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
                soup = BeautifulSoup(content, 'html.parser')
                text_content = soup.get_text()
                
                if re.search(search_term, text_content, re.IGNORECASE):
                    results.append({
                        'filename': filename,
                        'filepath': filepath,
                        'snippet': get_snippet(text_content, search_term)
                    })
    
    return results

def get_snippet(text, search_term, context=50):
    index = text.lower().find(search_term.lower())
    start = max(0, index - context)
    end = min(len(text), index + len(search_term) + context)
    return text[start:end].strip()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('query', '')
    if query:
        results = search_webpages(query)
    else:
        results = []
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
