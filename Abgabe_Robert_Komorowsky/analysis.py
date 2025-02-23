from typing import List, Dict, Any
import json
import os
from datetime import datetime
import pandas as pd
from collections import Counter

def total_publications(processed_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Berechnet die Anzahl der Publikationen pro Jahr.
    
    :param processed_data: Liste der verarbeiteten Publikationen.
    :return: Dictionary mit der Gesamtanzahl der Publikationen und der Anzahl pro Jahr.
    """
    analysis = {"total": len(processed_data), "by_year": {}}
    for paper in processed_data:
        year = paper.get("Year")
        if year != "N/A":
            analysis["by_year"][year] = analysis["by_year"].get(year, 0) + 1
    return analysis

def compute_publication_stats(processed_data: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Berechnet die Häufigkeit von Publikationstypen über alle Paper.
    
    :param processed_data: Liste der verarbeiteten Publikationen.
    :return: Dictionary mit den Publikationstypen als Schlüssel und deren Häufigkeit als Wert.
    """
    keywords = []
    for paper in processed_data:
        pub_types = paper.get("PublicationTypes", "")
        if pub_types and pub_types != "N/A":
            keywords.extend([word.strip() for word in pub_types.split(",")])
    return dict(Counter(keywords))

def compute_journal_stats(processed_data: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Berechnet die Häufigkeit von Journals über alle Journaleinträge.
    
    :param processed_data: Liste der verarbeiteten Publikationen.
    :return: Dictionary mit Journalnamen als Schlüssel und deren Häufigkeit als Wert.
    """
    journals = []
    for paper in processed_data:
        journal_name = paper.get("Journal", "").strip()
        if journal_name and journal_name != "N/A":
            journals.append(journal_name)  # Keine Auftrennung an Kommata
    return dict(Counter(journals))

def save_results(processed_data: List[Dict[str, Any]], metadata: Dict[str, Any]) -> None:
    """
    Speichert die verarbeiteten Ergebnisse und die Metadaten in separaten JSON-Dateien mit Zeitstempel.
    
    :param processed_data: Liste der verarbeiteten Publikationen.
    :param metadata: Dictionary mit zusätzlichen Metadaten.
    """
    print("Speichere Ergebnisse und Metadaten...")
    os.makedirs("data", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    results_filename = f"literature_search_results_{timestamp}.json"
    results_filepath = os.path.join("data", results_filename)
    with open(results_filepath, "w", encoding="utf-8") as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=4)
    
    metadata_filename = f"literature_search_metadata_{timestamp}.json"
    metadata_filepath = os.path.join("data", metadata_filename)
    with open(metadata_filepath, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=4)

    print(f"Ergebnisse wurden in '{results_filepath}' gespeichert.")
    print(f"Metadaten wurden in '{metadata_filepath}' gespeichert.")

def display_results(processed_data: List[Dict[str, Any]]) -> None:
    """
    Gibt die verarbeiteten Ergebnisse als Pandas DataFrame aus.
    
    :param processed_data: Liste der verarbeiteten Publikationen.
    """
    df = pd.DataFrame(processed_data)
    
    if df.empty:
        print("Keine Publikationen gefunden.")
    else:
        print("\n Extrahierte Publikationen:")
        print(df)
