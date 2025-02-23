from typing import List, Dict, Any
import os
import json

from pdf_manipulations.pdf_downloader import download_pdfs, sanitize_filename
from pdf_manipulations.pdf_vectorization import vectorising_pdfs
from rag.query_to_cohere import query_to_cohere

OUTPUT_DIR = "pdf_manipulations"
METADATA_FILE = os.path.join(OUTPUT_DIR, "metadata.json")

def extract_metadata(paper: Dict[str, Any]) -> Dict[str, str]:
    """
    Extrahiert relevante Metadaten für ein Paper.

    :param paper: Ein Dictionary mit den Paper-Daten.
    :return: Ein Dictionary mit extrahierten Metadaten (Titel, Autoren, DOI, Abstract).
    """
    return {
        "Title": paper.get("title", "N/A"),
        "Authors": ", ".join(author.get("name", "N/A") for author in paper.get("authors", [])),
        "DOI": paper.get("externalIds", {}).get("DOI", "N/A"),
        "Abstract": paper.get("abstract", "N/A")
    }

def save_metadata_incrementally(paper: Dict[str, Any]):
    """
    Speichert Metadaten eines Papers schrittweise in metadata.json, ohne die Datei zu überschreiben.

    :param paper: Ein Dictionary mit den Paper-Daten.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            try:
                metadata_list = json.load(f)
                if not isinstance(metadata_list, list):
                    metadata_list = []
            except json.JSONDecodeError:
                metadata_list = []
    else:
        metadata_list = []

    metadata_list.append(extract_metadata(paper))

    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata_list, f, indent=4, ensure_ascii=False)

def enrich_with_ai_analysis(papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Führt eine KI-Analyse durch und ergänzt die Paper-Daten um die Ergebnisse.
    Die Analyse erfolgt mit Cohere's API und generiert Antworten auf folgende Fragen:
    - Forschungsfrage des Papers
    - Ziel des Papers
    - Hauptbeitrag des Papers
    Es wird ein API-Key von Cohere benötigt, Rate Limits siehe https://docs.cohere.com/v2/docs/rate-limits.
    Die RAG-Analyse erfolgt mittels Code aus dem Capstone Project: Retrieval-Augmented Generation (RAG) System for Academic Papers
    Quelle: https://github.com/ArtashesMezhlumyan/RAG_for_papers

    :param papers: Eine Liste von Paper-Dictionaries.
    :return: Die Liste der Paper-Dictionaries mit angereicherten KI-Analysen.
    """
    for paper in papers:
        pdf_title = sanitize_filename(paper["Title"])
        
        print(f"Führe AI-Analyse durch für: {pdf_title}")

        research_question = query_to_cohere("What is the research question of the paper?", pdf_title)
        objective = query_to_cohere("What is the objective of the paper?", pdf_title)
        contribution = query_to_cohere("What is the main contribution of the paper?", pdf_title)

        paper["AI_analysis"] = {
            "Research Question": research_question,
            "Objective": objective,
            "Contribution": contribution
        }
    
    print("AI-Analyse abgeschlossen.")
    return papers

def process_papers(papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Verarbeitet Publikationen, speichert Metadaten, lädt PDFs herunter und erzeugt Embeddings.

    - Extrahiert relevante Felder aus den Paper-Daten.
    - Falls ein Open-Access-PDF vorhanden ist, wird es heruntergeladen.
    - Die Vektorisierung der PDFs erfolgt zur späteren RAG-Nutzung.
    - Die Papers werden mit KI-Analysen angereichert.

    Verwendete API-Felder:
    - title: Der Titel der Publikation.
    - authors: Liste von Autoren, deren Namen als kommaseparierte Zeichenkette dargestellt werden.
    - year: Das Erscheinungsjahr der Publikation.
    - abstract: Die Zusammenfassung der Publikation.
    - url: Der Link zur Publikation auf Semantic Scholar.
    - externalIds: Ein Dictionary externer IDs (z. B. DOI).
         * Der DOI wird über den Schlüssel "DOI" extrahiert.
    - citationCount: Die Anzahl der Zitationen.
    - referenceCount: Die Anzahl der Referenzen im Literaturverzeichnis.
    - isOpenAccess: Boolescher Wert, der angibt, ob die Publikation Open Access ist.
    - openAccessPdf: Falls vorhanden, enthält dieses Feld ein Dictionary mit der URL zum Open-Access-PDF.
         * Es wird die URL über den Schlüssel "url" extrahiert.
    - publicationTypes: Eine Liste, die den Publikationstyp beschreibt. Diese wird als kommaseparierte Zeichenkette ausgegeben.
    - journal: Ein Objekt mit Informationen zur Zeitschrift. Es wird der Name des Journals (über den Schlüssel "name") extrahiert.
    - tldr: Dieses Feld enthält eine Kurzfassung der Publikation.
         * Falls tldr ein Dictionary ist, wird nur der Wert unter dem Schlüssel "text" extrahiert.
    
    Fehlende oder nicht verfügbare Felder werden durch den Wert "N/A" ersetzt.

    :param papers: Eine Liste von Paper-Dictionaries.
    :return: Die Liste der Paper-Dictionaries mit verarbeiteten Daten und KI-Analysen.
    """
    
    if os.path.exists(METADATA_FILE):
        os.remove(METADATA_FILE)

    print(f"Beginne Verarbeitung von {len(papers)} Publikationen...")

    processed = []
    pdf_urls = []
    pdf_titles = []

    for index, paper in enumerate(papers, start=1):
        print(f"Verarbeite Paper {index}/{len(papers)}: {paper.get('title', 'Unbekannter Titel')}")
        
        save_metadata_incrementally(paper)

        title = paper.get("title", "N/A")
        authors = ", ".join(author.get("name", "N/A") for author in paper.get("authors", []))
        year = paper.get("year", "N/A")
        doi = paper.get("externalIds", {}).get("DOI", "N/A")
        url = paper.get("url", "N/A")
        abstract = paper.get("abstract", "N/A")
        
        open_access_pdf = paper.get("openAccessPdf") or {}
        open_access_pdf_url = open_access_pdf.get("url", "N/A")
        
        citation_count = paper.get("citationCount", "N/A")
        reference_count = paper.get("referenceCount", "N/A")
        is_open_access = paper.get("isOpenAccess", False)
        publication_types_str = ", ".join(paper.get("publicationTypes", [])) if paper.get("publicationTypes") else "N/A"
        journal_name = paper.get("journal", {}).get("name", "N/A")
        tldr_text = paper.get("tldr", {}).get("text", "N/A") if isinstance(paper.get("tldr"), dict) else paper.get("tldr", "N/A")

        if open_access_pdf_url != "N/A":
            pdf_urls.append(open_access_pdf_url)
            pdf_titles.append(sanitize_filename(title))

        processed.append({
            "Title": title,
            "Authors": authors,
            "Year": year,
            "DOI": doi,
            "URL": url,
            "Abstract": abstract,
            "Citation Count": citation_count,
            "Reference Count": reference_count,
            "isOpenAccess": is_open_access,
            "OpenAccessPDF": open_access_pdf_url,
            "PublicationTypes": publication_types_str,
            "Journal": journal_name,
            "TLDR": tldr_text,
            "AI_analysis": {
                "Research Question": "N/A",
                "Objective": "N/A",
                "Contribution": "N/A"
            }
        })

    if pdf_urls:
        print(f"Lade {len(pdf_urls)} PDFs herunter...")
        download_pdfs(pdf_urls, pdf_titles)

    print("Starte Vektorisierung der PDFs...")
    vectorising_pdfs()

    print("Starte AI-gestützte Analyse...")
    processed = enrich_with_ai_analysis(processed)

    print(f"Verarbeitung abgeschlossen. {len(processed)} Publikationen verarbeitet.")
    return processed