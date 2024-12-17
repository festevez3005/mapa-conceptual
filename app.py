# Instalar librerías necesarias
# Estas líneas aseguran la instalación del modelo si no está presente
import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import spacy
except ModuleNotFoundError:
    install("spacy")
    install("networkx")
    install("matplotlib")
    install("streamlit")
    subprocess.run([sys.executable, "-m", "spacy", "download", "es_core_news_sm"])
    import spacy

import networkx as nx
import matplotlib.pyplot as plt
from spacy.lang.es.stop_words import STOP_WORDS
import streamlit as st
from io import BytesIO

# Cargar el modelo de spaCy en español
@st.cache_resource
def load_model():
    try:
        return spacy.load("es_core_news_sm")
    except OSError:
        subprocess.run([sys.executable, "-m", "spacy", "download", "es_core_news_sm"])
        return spacy.load("es_core_news_sm")

nlp = load_model()

def extract_concepts_and_relations(text):
    """
    Extrae conceptos y relaciones a partir de un texto usando spaCy.
    Devuelve una lista de nodos (conceptos) y aristas (relaciones).
    """
    doc = nlp(text)
    nodes = set()  # Almacena conceptos únicos
    edges = []     # Almacena relaciones

    # Extraer sustantivos y verbos como conceptos clave
    for token in doc:
        if token.pos_ in {"NOUN", "PROPN"} and token.text.lower() not in STOP_WORDS:
            nodes.add(token.text)
            # Relacionar sustantivos con verbos cercanos
            for child in token.children:
                if child.pos_ == "VERB":
                    nodes.add(child.text)
                    edges.append((token.text, child.text))
                elif child.pos_ == "NOUN":
                    edges.append((token.text, child.text))

    return list(nodes), edges

def plot_concept_map(nodes, edges):
    """
    Genera y visualiza un mapa conceptual usando NetworkX y devuelve la imagen.
    """
    G = nx.DiGraph()  # Grafo dirigido

    # Agregar nodos y aristas
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)

    # Configurar el layout
    pos = nx.spring_layout(G, k=0.5)

    # Dibujar el grafo
    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=3000, font_size=10, font_weight='bold', arrows=True)
    plt.title("Mapa Conceptual Generado", fontsize=15)

    # Guardar la imagen en memoria
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    return buffer

# Interfaz de Streamlit
st.title("Generador de Mapas Conceptuales")
st.write("Ingrese un texto para analizar y generar un mapa conceptual.")

# Input de texto del usuario
texto = st.text_area("Texto de entrada:", "La bicicleta es un medio de transporte ecológico. Los ciclistas disfrutan de paseos por la montaña.")

if st.button("Generar Mapa Conceptual"):
    if texto:
        # Extraer conceptos y relaciones
        nodos, aristas = extract_concepts_and_relations(texto)

        # Mostrar resultados
        st.subheader("Conceptos (nodos):")
        st.write(nodos)

        st.subheader("Relaciones (aristas):")
        st.write(aristas)

        # Generar y mostrar el mapa conceptual
        st.subheader("Mapa Conceptual:")
        image_buffer = plot_concept_map(nodos, aristas)
        st.image(image_buffer, caption="Mapa Conceptual Generado", use_column_width=True)
    else:
        st.warning("Por favor, ingrese un texto para analizar.")
