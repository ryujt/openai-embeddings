import os
import requests
import numpy as np
import json
import nltk
from nltk.tokenize import word_tokenize

# API 설정
API_KEY = '[Your API Key]'
MODEL = 'text-embedding-3-large'
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
EMBEDDING_API_URL = "https://api.openai.com/v1/embeddings"
CHAT_API_URL = "https://api.openai.com/v1/chat/completions"
EMBEDDINGS_FILE = 'embeddings.jsonl'

def load_embeddings():
    embeddings = {}
    with open(EMBEDDINGS_FILE, 'r', encoding='utf-8') as file:
        for line in file:
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

def find_most_similar(text):
    input_embedding = get_embedding(text)
    embeddings_data = load_embeddings()
    similarities = {}
    
    for filename, data in embeddings_data.items():
        similarity = cosine_similarity(input_embedding, data['embedding'])
        similarities[filename] = similarity

    # Sort files by similarity in descending order and get the top 10
    sorted_files = sorted(similarities.items(), key=lambda item: item[1], reverse=True)[:10]
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

# Example usage
if __name__ == "__main__":
    user_input = """SQL 관련 패킷을 UDP로 수신받아서 처리하는 부분에 대해서 설명해줘."""
    similar_files = find_most_similar(user_input)

    nltk.download('punkt')    
    
    token_total = 0
    prompt = user_input + "\n\n"
    
    for i, (filename, similarity) in enumerate(similar_files, 1):
        content = load_embeddings()[filename]['content']
        token_count = count_tokens(content)
        token_total += token_count
        if token_total > 120 * 1024:
            break

        prompt += f"### 참고자료 {i}\n{content}\n\n"

    print("Sending prompt to OpenAI...")
    response = ask_openai(prompt)
    print("OpenAI Response received. Saving to response.md...")

    # 답변을 response.md 파일로 저장
    with open('response.md', 'w', encoding='utf-8') as file:
        file.write(response)

    print("Response saved to response.md")