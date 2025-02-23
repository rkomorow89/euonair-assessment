import sys
from research import build_query, search_semantic_scholar
from extraction import process_papers
from analysis import total_publications, compute_publication_stats, compute_journal_stats, save_results, display_results

def main(required_terms, or_terms, not_terms, start_year, end_year, last_n_years, limit, open_access_only, pdf_available_only) -> None:
    """
    Führt eine automatisierte Literaturrecherche durch, analysiert die Ergebnisse und speichert die Analyse.

    Die Funktion führt folgende Schritte aus:
    1. Erstellung einer Suchanfrage basierend auf den gegebenen Schlüsselwörtern und Filtern.
    2. Durchführung einer Suche in Semantic Scholar nach relevanten wissenschaftlichen Publikationen.
    3. Extraktion relevanter Informationen aus den gefundenen Publikationen.
    4. Analyse der Ergebnisse (z. B. Anzahl der Publikationen pro Jahr, häufige Publikationstypen, Journal-Statistiken).
    5. Speicherung und Anzeige der Analyse-Ergebnisse.

    Parameter:
    - required_terms (list): Liste der Begriffe, die in jeder Publikation enthalten sein müssen.
    - or_terms (list): Liste der Begriffe, von denen mindestens einer in der Publikation vorkommen sollte.
    - not_terms (list): Liste der Begriffe, die in den Publikationen nicht vorkommen dürfen.
    - start_year (int | None): Startjahr der Suche (nur falls last_n_years nicht angegeben ist).
    - end_year (int | None): Endjahr der Suche (nur falls last_n_years nicht angegeben ist).
    - last_n_years (int | None): Anzahl der letzten Jahre, aus denen Publikationen berücksichtigt werden sollen.
    - limit (int): Maximale Anzahl an zurückgegebenen Publikationen (Standard: 10).
    - open_access_only (bool): Falls True, werden nur Open-Access-Publikationen berücksichtigt.
    - pdf_available_only (bool): Falls True, werden nur Publikationen mit verfügbarem PDF berücksichtigt.

    Rückgabewert:
    - None
    """
    print("Starte Literaturrecherche...")

    query = build_query(required_terms, or_terms, not_terms)

    if last_n_years:
        papers = search_semantic_scholar(
            query,
            last_n_years=last_n_years,
            limit=limit,
            open_access_only=open_access_only,
            pdf_available_only=pdf_available_only
        )
    else:
        papers = search_semantic_scholar(
            query,
            start_year=start_year,
            end_year=end_year,
            limit=limit,
            open_access_only=open_access_only,
            pdf_available_only=pdf_available_only
        )
    
    processed_data = process_papers(papers)
    
    publications_results = total_publications(processed_data)
    publication_stats = compute_publication_stats(processed_data)
    journal_stats = compute_journal_stats(processed_data)
    
    metadata = {
        "search_parameters": {
            "required_terms": required_terms,
            "or_terms": or_terms,
            "not_terms": not_terms,
            "start_year": start_year,
            "end_year": end_year,
            "last_n_years": last_n_years,
            "open_access_only": open_access_only,
            "pdf_available_only": pdf_available_only,
            "query": query
        },
        "analysis": {
            "total_publications": publications_results.get("total", 0),
            "publications_per_year": publications_results.get("by_year", {}),
            "frequent_publication_types": publication_stats,
            "frequent_journal_types": journal_stats
        }
    }
    
    print("\nAnalyse-Ergebnisse:")
    print(metadata["analysis"])
    
    display_results(processed_data)
    save_results(processed_data, metadata)

if __name__ == "__main__":

    required_terms = sys.argv[1].split(",") if sys.argv[1] else []
    or_terms = sys.argv[2].split(",") if len(sys.argv) > 2 and sys.argv[2] else []
    not_terms = sys.argv[3].split(",") if len(sys.argv) > 3 and sys.argv[3] else []
    start_year = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4].isdigit() else None
    end_year = int(sys.argv[5]) if len(sys.argv) > 5 and sys.argv[5].isdigit() else None
    last_n_years = int(sys.argv[6]) if len(sys.argv) > 6 and sys.argv[6].isdigit() else None
    limit = int(sys.argv[7]) if len(sys.argv) > 7 and sys.argv[7].isdigit() else 10
    open_access_only = sys.argv[8].lower() == "ja" if len(sys.argv) > 8 else False
    pdf_available_only = sys.argv[9].lower() == "ja" if len(sys.argv) > 9 else False
    
    main(required_terms, or_terms, not_terms, start_year, end_year, last_n_years, limit, open_access_only, pdf_available_only)
