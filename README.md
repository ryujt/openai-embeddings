# Source Code Embedding and Query System

This project provides a system for embedding source code files and generating responses to user queries using relevant code sections through the OpenAI API.

## Components

1. `emb_save.py`: Script for embedding and saving source code files
2. `emb_ask.py`: Script for finding relevant code based on user queries and generating responses via OpenAI API

## Usage

### 1. Environment Setup

- Ensure Python 3.x is installed.
- Install required libraries:

```
pip install requests numpy nltk
```

- Obtain an OpenAI API key from the [OpenAI website](https://openai.com/).

### 2. Source Code Embedding (emb_save.py)

1. Open `emb_save.py` and modify the following settings:
 - `API_KEY`: Enter your OpenAI API key.
 - `FOLDER_PATH`: Specify the path to the folder containing source code files to be embedded.
 - `EXTENSIONS`: Modify the file extensions to be processed as needed.

2. Run the script:

```
python emb_save.py
```

3. Upon completion, an `embeddings.jsonl` file will be generated.

### 3. Querying (emb_ask.py)

1. Open `emb_ask.py` and set `API_KEY` to your OpenAI API key.

2. Run the script:

```
python emb_ask.py
```

3. Enter your question at the user_input.

4. The generated response will be saved in a `response.md` file.

## Important Notes

- Securely manage your API key. Do not upload it to public repositories.
- Be mindful of API usage and associated costs.
- Processing large codebases may take considerable time.

## License

This project is provided under the [MIT License](LICENSE).

## Contributing

We welcome all contributions, including bug reports, feature suggestions, and pull requests.