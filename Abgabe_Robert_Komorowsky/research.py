from typing import List, Dict, Any, Union, Optional
import requests
from datetime import datetime
import time

def build_query(required_terms: Union[List[str], str],
                or_terms: Optional[List[str]] = None,
                not_terms: Optional[List[str]] = None) -> str:
    """
    Konstruiert einen Such-Query-String basierend auf den übergebenen Begriffen.
    """
    if isinstance(required_terms, list):
        query = " AND ".join(f'("{term}")' for term in required_terms)
    else:
        query = f'("{required_terms}")'
    
    if or_terms:
        or_query = " OR ".join(f'("{term}")' for term in or_terms)
        query = f"{query} OR {or_query}"
    
    if not_terms:
        not_query = " NOT ".join(f'("{term}")' for term in not_terms)
        query = f"{query} NOT {not_query}"
    
    return query

def search_semantic_scholar(query: str,
                            start_year: Optional[int] = None,
                            end_year: Optional[int] = None,
                            last_n_years: Optional[int] = None,
                            limit: int = 10,
                            open_access_only: bool = False,
                            pdf_available_only: bool = False) -> List[Dict[str, Any]]:
    """
    Sucht Publikationen über die Semantic Scholar API und sammelt bis zu 'limit' eindeutige Ergebnisse.
    API-Dokumentation: https://api.semanticscholar.org/api-docs/
    API-Lizenzvereinbarung: https://www.semanticscholar.org/product/api/license

    Optionen:
      - start_year/end_year: Filtert Ergebnisse nach einem bestimmten Zeitraum.
      - last_n_years: Berechnet den Zeitraum basierend auf den letzten n Jahren.
      - limit: Anzahl der angeforderten Publikationen pro API-Aufruf
      - open_access_only: Falls True, werden nur Open-Access-Publikationen zurückgegeben.
      - pdf_available_only: Falls True, werden nur Publikationen zurückgegeben, bei denen
                            ein Open-Access-PDF verfügbar ist.
    
    Es wird innerhalb von 1 Minute gesucht, um die gewünschte Anzahl an eindeutigen Ergebnissen zu sammeln.
    """
    print("Starte Suche mit Query:", query)
    if last_n_years is not None:
        current_year = datetime.now().year
        start_year = current_year - last_n_years
        end_year = current_year

    base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
    accumulated_results: List[Dict[str, Any]] = []
    seen_ids = set()
    offset = 0
    start_time = time.time()

    fields = ("paperId,title,authors,year,abstract,url,externalIds,"
              "citationCount,referenceCount,isOpenAccess,openAccessPdf,"
              "publicationTypes,journal,tldr")
    
    while len(accumulated_results) < limit and (time.time() - start_time < 60):
        params = {
            "query": query,
            "limit": limit,
            "offset": offset,
            "fields": fields
        }
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            results = response.json().get('data', [])
            print("Erfolgreiche API-Antwort erhalten. Anzahl gefundener Publikationen:", len(results))
            if not results:
                print("Keine weiteren Ergebnisse gefunden. Beende Suche.")
                break

            if start_year or end_year:
                filtered_results = []
                for paper in results:
                    year = paper.get('year')
                    if year:
                        if start_year and year < start_year:
                            continue
                        if end_year and year > end_year:
                            continue
                        filtered_results.append(paper)
                results = filtered_results
                print("Nach Zeitraum gefiltert. Verbleibende Publikationen:", len(results))

            if open_access_only:
                results = [paper for paper in results if paper.get('isOpenAccess', False)]
                print("Nach Open-Access gefiltert. Verbleibende Publikationen:", len(results))
            
            if pdf_available_only:
                results = [paper for paper in results 
                           if paper.get('openAccessPdf') and paper.get('openAccessPdf').get('url')]
                print("Nach PDF-Verfügbarkeit gefiltert. Verbleibende Publikationen:", len(results))
            
            unique_results = []
            for paper in results:
                uid = paper.get("paperId")
                if uid and uid not in seen_ids:
                    seen_ids.add(uid)
                    unique_results.append(paper)
            
            accumulated_results.extend(unique_results)
            print("Anzahl gespeicherter einzigartiger Publikationen:", len(accumulated_results))

            #offset += len(results)
            offset += limit
        elif response.status_code == 429:
            print("Rate limit erreicht (429). Warte 10 Sekunden...")
            time.sleep(10)
        else:
            print("Fehler bei der Anfrage:", response.status_code)
            break

    return accumulated_results[:limit]
