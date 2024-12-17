import requests
from bs4 import BeautifulSoup
import spacy
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter
import re
import streamlit as st

def crawl_page(url):
    """Crawl the page and extract text content."""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract visible text from the page
        text = ' '.join([t.get_text() for t in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])])
        return text
    except Exception as e:
        st.error(f"Error crawling page: {e}")
        return None

def clean_text(text):
    """Clean and preprocess text."""
    text = re.sub(r'\s+', ' ', text)  # Remove extra spaces
    text = re.sub(r'[^a-zA-Z0-9\sÀ-ÿ]', '', text)  # Remove special characters, allow accented characters
    return text

def analyze_content(text, language):
    """Analyze content and extract main terms with NLP."""
    if language == 'es':
        nlp = spacy.load("
