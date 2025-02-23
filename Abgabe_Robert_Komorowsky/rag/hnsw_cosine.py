from hnswlib import Index
from typing import List, Tuple
from sentence_transformers import SentenceTransformer
import pickle
import hnswlib
import torch
import warnings
from urllib3.exceptions import InsecureRequestWarning
from pathlib import Path


warnings.filterwarnings("ignore", category=InsecureRequestWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

model = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')

def search_within_pdfs(query: str, selected_pdfs: List[str], k: int = 10) -> List[Tuple[str, float, str]]:
    """
    Durchsucht ausgewählte PDF-Dokumente nach Absätzen, die semantisch zur Suchanfrage passen.

    Args:
        query (str): Die Suchanfrage als Text.
        selected_pdfs (List[str]): Liste der zu durchsuchenden PDF-Dateien anhand ihrer IDs.
        k (int, optional): Anzahl der zurückzugebenden relevantesten Absätze. Standard ist 10.

    Returns:
        List[Tuple[str, float, str]]: Eine Liste von Tupeln, die den gefundenen Absatztext,
        den Ähnlichkeitswert (zwischen 0 und 1) und die zugehörige PDF-ID enthalten.
    """

    embedding_path = Path(__file__).parent / "../pdf_manipulations/pdf_paragraphs_embeddings.pkl"
    
    if not embedding_path.exists():
        print("Die Embeddings-Datei wurde nicht gefunden! Stelle sicher, dass du die PDFs vektorisiert hast.")
        return []
    
    with open(embedding_path, "rb") as fIn:
        stored_data = pickle.load(fIn)

    available_pdfs = set(stored_data["pdf_id"])

    if selected_pdfs[0] not in available_pdfs:
        print(f"Das ausgewählte PDF '{selected_pdfs[0]}' wurde nicht gefunden! Keine Embeddings erstellt.")
        return []

    returning_list = []
    for i in range(len(selected_pdfs)):
        next = selected_pdfs[i]
        selected_ids = [next]
        filtered_pdf_id_order = [uniq for id_, uniq in zip(stored_data["pdf_id"], stored_data["embedding"]) if id_ in selected_ids]
        filtered_pdf_ids = [id_ for id_ in stored_data["pdf_id"] if id_ in selected_ids]
        filtered_pdf_paragraph_embeddings = [embed for id_, embed in zip(stored_data["pdf_id"], stored_data["embedding"]) if id_ in selected_ids]
        filtered_pdf_paragraph_text = [text for id_, text in zip(stored_data["pdf_id"], stored_data["paragraph_text"]) if id_ in selected_ids]
        filtered_pdf_paragraph_embeddings = torch.tensor(filtered_pdf_paragraph_embeddings)
        
        if isinstance(filtered_pdf_paragraph_embeddings, torch.Tensor):
            filtered_pdf_paragraph_embeddings = filtered_pdf_paragraph_embeddings.cpu().numpy()  

        if len(filtered_pdf_paragraph_embeddings) == 0:
            print(f"Keine Embeddings für das ausgewählte PDF gefunden: {selected_pdfs}")
            return []

        dimension = filtered_pdf_paragraph_embeddings.shape[1]
        p = hnswlib.Index(space='cosine', dim=dimension)
        p.init_index(max_elements=10000, ef_construction=200, M=16)
        p.add_items(filtered_pdf_paragraph_embeddings)  
        p.set_ef(50)  

        query_embedding = model.encode([query])

        labels, distances = p.knn_query(query_embedding, k=k)
        similar_sentences_with_scores = [(filtered_pdf_paragraph_text[label], 1 - distance, str(filtered_pdf_ids[label])) for label, distance in zip(labels[0], distances[0])]
        returning_list+=similar_sentences_with_scores

    return returning_list



