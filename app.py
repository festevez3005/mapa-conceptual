import requests
from bs4 import BeautifulSoup
import spacy
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter
import re
import streamlit as st
from spacy.cli import download

# Function to load spaCy models safely
def load_spacy_model(language):
    try:
        if language == 'es':
            nlp = spacy.load("es_core_news_sm")
        else:
            nlp = spacy.load("en_core_web_sm")
        return nlp
    except OSError:
        st.error("spaCy model not found. Downloading...")
        try:
            download("en_core_web_sm")
            download("es_core_news_sm")
            nlp = spacy.load("en_core_web_sm" if language == 'en' else "es_core_news_sm")
            return nlp
        except Exception as e:
            st.error(f"Error downloading spaCy models: {e}")
            return None

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
    nlp = load_spacy_model(language)
    if not nlp:
        return None, None

    doc = nlp(text)

    # Extract nouns and proper nouns as main terms
    terms = [token.text.lower() for token in doc if token.pos_ in ('NOUN', 'PROPN') and not token.is_stop]

    # Count term frequency
    term_freq = Counter(terms)

    # Identify relationships (co-occurrences in sentences)
    relationships = []
    for sent in doc.sents:
        sent_terms = [token.text.lower() for token in sent if token.pos_ in ('NOUN', 'PROPN') and not token.is_stop]
        for i, term1 in enumerate(sent_terms):
            for term2 in sent_terms[i + 1:]:
                relationships.append((term1, term2))

    return term_freq, relationships

def create_conceptual_map(term_freq, relationships):
    """Generate and display a conceptual map using NetworkX."""
    G = nx.Graph()

    # Add nodes with size based on frequency
    for term, freq in term_freq.items():
        G.add_node(term, size=freq * 100)

    # Add edges for relationships
    for term1, term2 in relationships:
        if G.has_edge(term1, term2):
            G[term1][term2]['weight'] += 1
        else:
            G.add_edge(term1, term2, weight=1)

    # Draw the graph
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, k=0.5)
    sizes = [G.nodes[node]['size'] for node in G.nodes]
    nx.draw(G, pos, with_labels=True, node_size=sizes, font_size=10, font_color='black', edge_color='gray')
    plt.title("Conceptual Map")
    st.pyplot(plt)

def main():
    st.title("Conceptual Map Analyzer")

    # Initialize text variable to avoid UnboundLocalError
    text = None

    # Input options for URL or text
    choice = st.radio("Choose input type:", ("URL", "Raw Text"))

    if choice == "URL":
        url = st.text_input("Enter the URL to analyze:")
        if url:
            st.write("Crawling the page...")
            text = crawl_page(url)
            if text:
                st.write("Text successfully extracted from the URL.")
    else:
        text = st.text_area("Enter the raw text to analyze:")

    if text:
        # Language selection
        language = st.radio("Is the text in English (en) or Spanish (es)?", ('en', 'es'))
        
        st.write("Cleaning and analyzing content...")
        cleaned_text = clean_text(text)
        term_freq, relationships = analyze_content(cleaned_text, language)

        if term_freq is None or relationships is None:
            return

        st.write("\nTop Terms:")
        for term, freq in term_freq.most_common(10):
            st.write(f"{term}: {freq}")

        st.write("\nGenerating Conceptual Map...")
        create_conceptual_map(term_freq, relationships)
    else:
        st.warning("Please provide a URL or raw text to analyze.")

if __name__ == "__main__":
    main()
