# app.py
from flask import Flask, render_template, request
import json
import os
import requests
import numpy as np
import nltk
from nltk.tokenize import word_tokenize
import re

app = Flask(__name__)

# API 설정
API_KEY = '[Your API Key]'
MODEL = 'text-embedding-3-large'
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

EMBEDDING_API_URL = "https://api.openai.com/v1/embeddings"
CHAT_API_URL = "https://api.openai.com/v1/chat/completions"

def get_jsonl_files():
    return [f for f in os.listdir('.') if f.endswith('.jsonl')]

def load_embeddings(files):
    embeddings = {}
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line)
                embeddings[data['filename']] = {
                    'content': data['content'],
                    'embedding': data['embedding']
                }
    return embeddings

def get_embedding(text):
    data = json.dumps({
        "input": text,
        "model": MODEL,
        "encoding_format": "float"
    })
    response = requests.post(EMBEDDING_API_URL, headers=HEADERS, data=data)
    return response.json()['data'][0]['embedding']

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def find_most_similar(text, embeddings, similarity_threshold=0.25):
    input_embedding = get_embedding(text)
    similarities = {}
    
    for filename, data in embeddings.items():
        similarity = cosine_similarity(input_embedding, data['embedding'])
        if similarity >= similarity_threshold:
            similarities[filename] = similarity

    sorted_files = sorted(similarities.items(), key=lambda item: item[1], reverse=True)[:50]
    return sorted_files

def count_tokens(text):
    tokens = word_tokenize(text)
    return len(tokens)

def ask_openai(prompt):
    data = json.dumps({
        "model": "gpt-4o", 
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5
    })
    response = requests.post(CHAT_API_URL, headers=HEADERS, data=data)
    return response.json()['choices'][0]['message']['content']

@app.route('/', methods=['GET', 'POST'])
def index():
    jsonl_files = get_jsonl_files()
    
    if request.method == 'POST':
        selected_files = request.form.getlist('files')
        user_input = request.form['question']
        
        nltk.download('punkt', quiet=True)
        
        embeddings = load_embeddings(selected_files)
        similar_files = find_most_similar(user_input, embeddings)
        
        print("\n===== 유사도로 선택된 파일 =====")
        for filename, similarity in similar_files:
            print(f"{filename}: {similarity}")
        
        token_total = 0
        prompt = f"제공되는 참고자료를 토대로 대답해줘.\n{user_input}\n\n"
        
        used_files = []
        for i, (filename, similarity) in enumerate(similar_files, 1):
            content = embeddings[filename]['content']
            token_count = count_tokens(content)
            if token_total + token_count > 120 * 1024:
                break
            token_total += token_count
            prompt += f"### 참고자료 {i}\n{content}\n\n"
            used_files.append(filename)

        print(f"\n===== 프롬프트 생성 정보 =====")
        print(f"총 토큰 수: {token_total}")
        print(f"사용된 파일: {used_files}")

        print("\n===== OpenAI API 호출 중 =====")
        response = ask_openai(prompt)
        
        print("\n===== OpenAI 응답 정보 =====")
        print(f"응답 길이: {len(response)} 글자")

        return render_template('result.html', question=user_input, answer=response, selected_files=selected_files)
    
    return render_template('index.html', jsonl_files=jsonl_files)

if __name__ == '__main__':
    app.run(debug=True)