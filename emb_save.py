import os
import requests
import json

# API 설정
API_KEY = '[Your API Key]'
MODEL = 'text-embedding-3-large'
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
API_URL = "https://api.openai.com/v1/embeddings"

FOLDER_PATH = '[Target Folder Path]'
EXTENSIONS = ['.cs', '.cpp', '.h'] # Target file extensions
EMBEDDINGS_FILE = 'embeddings.jsonl'

def get_file_paths(folder_path, extensions):
    file_paths = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_paths.append(os.path.join(root, file))
    return file_paths

def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def get_embedding(text):
    data = json.dumps({
        "input": text,
        "model": MODEL,
        "encoding_format": "float"
    })
    response = requests.post(API_URL, headers=HEADERS, data=data)
    return response.json()['data'][0]['embedding']

def main():
    file_paths = get_file_paths(FOLDER_PATH, EXTENSIONS)
    with open(EMBEDDINGS_FILE, 'w', encoding='utf-8') as f:
        for file_path in file_paths:
            try:
                relative_path = os.path.relpath(file_path, FOLDER_PATH)
                print(f"* Processing {relative_path}")
                
                content = read_file(file_path)
                embedding = get_embedding(content)
                file_data = {
                    "filename": relative_path, 
                    "content": content,
                    "embedding": embedding
                }
                f.write(json.dumps(file_data, ensure_ascii=False) + '\n')
            except Exception as e:
                print(f"  - Error processing {file_path}: {str(e)}")

if __name__ == "__main__":
    main()
