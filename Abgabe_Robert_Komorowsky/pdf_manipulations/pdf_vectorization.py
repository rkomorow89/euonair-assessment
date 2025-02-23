from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import Dict, Optional
import pandas as pd
import os
import json
from pdf_manipulations.pdf_to_text import extract_cleaned_text
import re

model = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=20,
    length_function=len
)

def get_latest_pdf_folder(pdf_base_path: Optional[str] = None) -> Optional[str]:
    """
    Findet den neuesten Zeitstempel-Ordner im angegebenen Basisverzeichnis.
    
    :param pdf_base_path: Optionaler Basispfad zu den PDF-Verzeichnissen.
    :return: Pfad des neuesten Unterordners oder None, falls keiner existiert.
    """
    if pdf_base_path is None:
        pdf_base_path = os.path.join("pdf_manipulations", "pdf_db")

    try:
        subdirs = [os.path.join(pdf_base_path, d) for d in os.listdir(pdf_base_path) if os.path.isdir(os.path.join(pdf_base_path, d))]
        latest_folder = max(subdirs, key=os.path.getmtime) 
        print(f"Neuester PDF-Ordner: {latest_folder}")
        return latest_folder
    except (ValueError, FileNotFoundError):
        print("Kein PDF-Ordner gefunden oder Basisverzeichnis existiert nicht!")
        return None

def load_metadata(json_path: str) -> Dict[str, Dict]:
    """
    Lädt die Metadaten aus einer JSON-Datei und gibt ein Dictionary zurück.
    
    :param json_path: Pfad zur JSON-Datei mit den Metadaten.
    :return: Ein Dictionary mit Dateinamen als Schlüssel und Metadaten als Werte.
    """
    if not os.path.exists(json_path):
        return {}
    
    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    metadata_dict = {re.sub(r'[^\w\-_]', '_', entry["Title"]): entry for entry in data}
    
    return metadata_dict

def vectorising_pdfs() -> Optional[pd.DataFrame]:
    """
    Vektorisiert alle PDFs im neuesten Zeitstempel-Ordner.
    
    - Extrahiert Text aus PDFs
    - Teilt den Text in Absätze auf
    - Erstellt Embeddings für jeden Absatz
    - Speichert die Embeddings in einer Pickle-Datei
    
    :return: Ein DataFrame mit Absätzen und ihren Embeddings oder None bei Fehlern.
    """
    pdf_folder = get_latest_pdf_folder()  
    
    if not pdf_folder:
        print("Kein gültiger PDF-Ordner gefunden. Abbruch!")
        return
    
    metadata_path = os.path.join("pdf_manipulations", "metadata.json")
    metadata_dict = load_metadata(metadata_path)
    paragraphs_info = []

    if not metadata_dict:
        print(f"Keine Metadaten in {metadata_path} gefunden. Abbruch!")
        return None

    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]
    
    if not pdf_files:
        print("Keine PDFs im neuesten Ordner gefunden. Abbruch!")
        return
    
    output_path = os.path.join("pdf_manipulations", "pdf_paragraphs_embeddings.pkl")
    
    if os.path.exists(output_path):
        os.remove(output_path)

    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_folder, pdf_file)
        
        pdf_id = os.path.splitext(pdf_file)[0]  
        title = metadata_dict.get(pdf_id, {}).get("Title", pdf_id) 

        print(f'Vektorisiere PDF {pdf_id} - {title}...')
        
        try:
            text = extract_cleaned_text(pdf_path)
        except Exception as e:
            print(f'Fehler beim Extrahieren von Text aus {pdf_file}: {e}')
            text = f"Paper '{title}' konnte nicht verarbeitet werden."

        chunks = text_splitter.create_documents([text])
        chunk_texts = [str(chunk) for chunk in chunks]
        
        for j, chunk in enumerate(chunk_texts):
            encode_chunk = model.encode(chunk, convert_to_tensor=True)

            paragraphs_info.append({
                "pdf_id_order": f"{pdf_id}_{j}",
                "pdf_id": pdf_id,
                "title": title,
                "paragraph_text": chunk,
                "embedding": encode_chunk.cpu().numpy()
            })

    if not paragraphs_info:
        print("Keine Absätze zum Vektorisieren gefunden. Abbruch!")
        return None
    
    df_paragraphs = pd.DataFrame(paragraphs_info)
    os.makedirs(os.path.dirname(output_path), exist_ok=True) 
    df_paragraphs.to_pickle(output_path)
    print(f"Embeddings gespeichert unter: {output_path}")

    print(f"{len(paragraphs_info)} Absätze erfolgreich vektorisiert und gespeichert.")
    return df_paragraphs

# PDFs vektorisieren
#vectorising_pdfs()
