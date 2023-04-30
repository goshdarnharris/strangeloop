
from langchain import PromptTemplate, LLMChain
from langchain.callbacks.base import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from pyllamacpp.model import Model
from langchain.embeddings.huggingface_hub import HuggingFaceHubEmbeddings
from llama_index import LangchainEmbedding

from langchain.llms import GPT4All
from langchain import HuggingFaceHub
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI

import json

def load_api_key(filename, key):
    with open(filename, 'r') as f:
        api_key = json.load(f).get(key, None)
    if api_key is None:
        raise ValueError(f'No key {key} in {filename}')
    return api_key

def gpt_35_turbo(**kwargs):
    llm = ChatOpenAI(
        model_name = "gpt-3.5-turbo", 
        openai_api_key = load_api_key("keys.json", "openai"),
        **kwargs,
        verbose = True
    )
    return llm

def davinci_003(**kwargs):
    llm = OpenAI(
        model_name = "text-davinci-003", 
        openai_api_key = load_api_key("keys.json", "openai"),
        **kwargs,
        verbose = True
    )
    return llm

def gpt4all_alpaca():
    model_path = './strangeloop/models/alpaca-native-7B-4bit-ggjt.bin'
    llm = GPT4All(
        model=model_path, 
        n_threads = 8, 
        verbose = True
    )
    return llm

def huggingface_llama():
    return HuggingFaceHub(
        repo_id = "decapoda-research/llama-7b-hf", 
        huggingfacehub_api_token =  load_api_key("keys.json", "huggingface")
    )

def huggingface_embed():    
    #define embedding model
    embeddings = LangchainEmbedding(HuggingFaceHubEmbeddings(
        huggingfacehub_api_token = load_api_key("keys.json", "huggingface")
    ))
    return embeddings
