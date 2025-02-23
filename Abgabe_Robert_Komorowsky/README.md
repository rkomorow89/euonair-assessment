# 📚 Literaturrecherche mit Semantic Scholar

Dieses Projekt führt eine automatisierte Literaturrecherche durch, extrahiert relevante Informationen aus den gefundenen Publikationen und analysiert die Ergebnisse. Es nutzt die **Semantic Scholar API** zur Suche nach wissenschaftlichen Artikeln und verarbeitet die Daten mit **Python**.

## 📌 Features
- **Suchanfragen anpassen:** Erstellung komplexer Suchabfragen mit logischen Operatoren (AND, OR, NOT).
- **Publikationen abrufen:** Abfrage von Artikeln über die **Semantic Scholar API**.
- **PDF-Extraktion:** Herunterladen, Umwandeln und Verarbeiten von Open-Access-PDFs.
- **KI-gestützte Analyse:** Automatische Extraktion von Forschungsfragen, Zielen und Beiträgen mithilfe eines KI-Modells (unter Verwendung der Cohere API).
- **Vektorisierung:** Erstellung von Text-Embeddings für PDF-Inhalte.
- **Semantische Suche:** Suche nach relevanten Absätzen innerhalb der PDF-Inhalte anhand von Ähnlichkeitswerten.
- **Statistische Analyse:** Auswertung der Publikationen nach Jahr, Typ und Journal.
- **Ergebnisse speichern:** Speicherung der analysierten Daten als JSON-Dateien.

## 📂 Projektstruktur

```
├── research.py               # Erstellung der Suchanfragen und API-Kommunikation
├── extraction.py             # Extraktion relevanter Informationen aus den Papers, inklusive PDF-Download und KI-Analyse
├── analysis.py               # Analyse der Publikationsdaten (z. B. Publikationsjahr, Typ, Journal)
├── main.py                   # Hauptskript zur Durchführung der Literaturrecherche
├── tests.py                  # Unit-Tests für die Kernfunktionen
├── start_search.bat          # Batch-Datei zur benutzerfreundlichen Eingabe der Suchparameter
├── pdf_manipulations/        # Module zur PDF-Verarbeitung
│   ├── pdf_downloader.py     # Herunterladen von Open-Access-PDFs
│   ├── pdf_to_text.py        # Umwandlung von PDFs in bereinigten Text
│   ├── pdf_vectorization.py  # Vektorisierung der PDF-Texte in Form von Embeddings
│   ├── pdfminer/             # Unterordner mit Tools und Bibliotheken zur PDF-Verarbeitung
│   └── pdf_db/               # Unterordner zum Speichern der heruntergeladenen PDFs
└── rag/                      # Module für KI-gestützte Analyse
    ├── hnsw_cosine.py        # Semantische Suche in PDF-Text-Embeddings  
    └── query_to_cohere.py    # KI-gestützte Beantwortung von Forschungsfragen mittels Cohere API
```

## 🚀 Installation & Ausführung

### 1️⃣ Voraussetzungen
- **Python 3.8+**
- **Abhängigkeiten installieren:**
  ```bash
  pip install -r requirements.txt
  ```
- **Umgebungsvariablen konfigurieren:**
  Erstelle eine `.env`-Datei im Projektverzeichnis mit folgendem Inhalt:
  ```bash
  COHERE_API_KEY=dein_api_key
  ```
  Um einen API-Key von Cohere zu erzeugen, muss ein Account angelegt werden. Über das [Dashboard](https://dashboard.cohere.com/api-keys) können zwei Arten von API-Keys angelegt werden: Evaluation Keys (kostenlos, aber mit eingeschränkter Nutzung) und Production Keys (kostenpflichtig und mit deutlich weniger Einschränkungen). Es müssen [Rate Limits](https://docs.cohere.com/v2/docs/rate-limits) beachtet werden. Für dieses Projekt wurde ein Evaluation Key verwendet. Ein RateLimiter im Code verhindert eine Überlastung der API.

### 2️⃣ Starten der Recherche

#### Direkt über Python
```bash
python main.py "required_terms" "or_terms" "not_terms" start_year end_year/last_n_years limit open_access_only pdf_available_only
```
Beispiel 1:
```bash
python main.py "Large Language Models" "Machine Learning" "Reinforcement Learning" 2022 2024 None 10 ja ja
```

Beispiel 2:
```bash
python main.py "Retrieval Augmented Generation" "Machine Learning" "Reinforcement Learning" None None 5 10 ja nein
```

#### Über die Batch-Datei `start_search.bat`
Die Datei `start_search.bat` ermöglicht eine interaktive Eingabe der Suchparameter und startet `main.py` automatisch mit den gewählten Einstellungen.

Das Skript führt die folgenden Schritte durch:
1. Generiert eine Suchanfrage.
2. Ruft Publikationen über die **Semantic Scholar API** ab.
3. Extrahiert Informationen und wertet Open-Access-PDFs aus.
4. Analysiert die Publikationen sowohl statistisch als auch mit KI.
5. Speichert die Ergebnisse als JSON-Datei.

## 🛠 Anpassung der Suche

Die Suchparameter befinden sich in `main.py` und bestimmen, welche Publikationen abgerufen werden.

### 🔍 Erklärung der Suchparameter:

- **`required_terms`**: Diese Begriffe **müssen** in den Publikationen enthalten sein (AND-Bedingung).  
  - Beispiel: `"generative artificial intelligence"` **und** `"education"` müssen vorkommen.

- **`or_terms`**: Diese Begriffe sind **optional**, aber wenn sie enthalten sind, werden die Publikationen bevorzugt (OR-Bedingung).  
  - Beispiel: Falls `"machine learning"` im Titel oder Abstract vorkommt, wird das Paper eher aufgenommen.

- **`not_terms`**: Falls einer dieser Begriffe vorkommt, wird die Publikation ausgeschlossen (NOT-Bedingung).  
  - Beispiel: `"reinforcement learning"` kommt im Titel vor → Paper wird **nicht** berücksichtigt.

- **`start_year` / `end_year`**: Definieren den **Zeitraum** der gesuchten Publikationen.  
  - Beispiel: Nur Publikationen von **2020 bis 2024** werden berücksichtigt.

- **`last_n_years`**: Falls gesetzt, werden nur Publikationen aus den letzten `n` Jahren berücksichtigt.  
  - Beispiel: Falls `last_n_years = 5` und das aktuelle Jahr 2025 ist, dann werden nur Publikationen von **2020 bis 2025** berücksichtigt.

- **`limit`**: Maximale Anzahl der Suchergebnisse.  
  - Beispiel: Falls mehr als **10 Publikationen** gefunden werden, werden nur die ersten 10 zurückgegeben.

- **`open_access_only`**: Falls `True`, werden nur **frei zugängliche (Open Access)** Publikationen erfasst.  
  - Falls `False`, werden auch kostenpflichtige oder eingeschränkt zugängliche Artikel eingeschlossen.

- **`pdf_available_only`**: Falls `True`, werden nur Publikationen mit **direkt verfügbarem PDF** berücksichtigt.  
  - Falls `False`, können auch Publikationen ohne PDF in den Ergebnissen enthalten sein.

🔹 **Anpassungsbeispiel 1**: Falls du nur Open-Access-Publikationen mit direkt verfügbarem PDF zu `"Large Language Models"` oder `"Machine Learning"`, aber nicht `"Reinforcement Learning"`, von 2022 bis 2024 mit einer maximalen Anzahl von 10 suchst:

```bash
Geben Sie die Pflichtbegriffe ein (Komma getrennt): Large Language Models
Geben Sie alternative Begriffe ein (Komma getrennt): Machine Learning
Geben Sie auszuschließende Begriffe ein (Komma getrennt): Reinforcement Learning
Wollen Sie eine Suche nach Start- und Endjahr oder nach den letzten N Jahren durchführen?
Drücken Sie S für Start-/Endjahr oder E für die letzten N Jahre [S,E]?S
Startjahr der Suche: 2022
Endjahr der Suche: 2024
Maximale Anzahl der Ergebnisse: 10
Nur Open Access? (ja/nein): ja
Nur mit PDF? (ja/nein): ja
```

🔹 **Anpassungsbeispiel 2**: Falls du nur Open-Access-Publikationen auch ohne direkt verfügbare PDF zu `"Retrieval Augmented Generation"` aus den letzten fünf Jahren mit einer maximalen Anzahl von zehn suchst:
```bash
Geben Sie die Pflichtbegriffe ein (Komma getrennt): Retrieval Augmented Generation
Geben Sie alternative Begriffe ein (Komma getrennt):
Geben Sie auszuschließende Begriffe ein (Komma getrennt):
Wollen Sie eine Suche nach Start- und Endjahr oder nach den letzten N Jahren durchführen?
Drücken Sie S für Start-/Endjahr oder E für die letzten N Jahre [S,E]?E
Anzahl der letzten Jahre für die Suche: 5
Maximale Anzahl der Ergebnisse: 10
Nur Open Access? (ja/nein): ja
Nur mit PDF? (ja/nein): nein
```

## 🤖 **KI-Methodik**

Das System kombiniert NLP-Methoden zur Verarbeitung akademischer PDFs, semantische Suche und LLM-Integration. In diesem Projekt wurde Code angepasst, der für ein  **Retrieval-Augmented Generation (RAG)-System für akademische Paper** entwickelt wurde, wie im zugehörigen [Bericht](https://cse.aua.am/files/2024/05/Building-a-Retrieval-Augmented-Generation-RAG-System-for-Academic-Papers.pdf) beschrieben. 

Die Kernkomponenten umfassen:
- **PDF-Download**: Automatisierter Download in zeitgestempelten Ordnern. 
  - Für jede neue Suche wird ein eigenes Verzeichnis, das den aktuellen Zeitstempel als Dateinamen enthält, automatisch erzeugt. In diesem werden die heruntergeladenen PDFs mit dem Titel als Dateinamen gespeichert.

    ```
    pdf_manipulations/
    ├── pdf_db/
        ├── YYYYMMDD_HHMMSS/
            ├── title1.pdf
            ├── title2.pdf
    ```
  - ein Download kann manchmal auch fehlschlagen, selbst wenn eine URL in openAccessPdf verfügbar ist
- **Textverarbeitung**: Extraktion und Bereinigung von Text aus PDFs.
- **Vektorisierung**: Embedding-Erstellung für PDF-Absätze mit `SentenceTransformer`.
  - die zugehörige Pickle-Datei wird gespeichert in
    ```
    pdf_manipulations/
    ├── pdf_paragraphs_embeddings.pkl
    ```
  - eine bestehende Pickle-Datei wird überschrieben
- **Semantische Suche**: Effiziente Ähnlichkeitssuche mittels HNSW (anhand Cosinus-Ähnlichkeit).
- **Cohere-Integration**: Generierung kontextbasierter Antworten durch LLMs.
---

### 1. **Embedding-Erstellung**
- **Modell**: `multi-qa-MiniLM-L6-cos-v1` (Sentence Transformers).
- **Textaufteilung**: 
  - `RecursiveCharacterTextSplitter` für Chunks (500 Zeichen, Overlap 20).
  - Aggregation durch **Mittelwertbildung** der absatzweisen Chunk-Embeddings der PDFs.
- **Speicherung**: Embeddings werden in `.pkl`-Dateien mit IDs und Texten gespeichert.

### 2. **Semantische Suche**
- **HNSW-Index (Hierarchical Navigable Small World)**: Hierarchischer Index für schnelle Nachbarschaftssuche (anhand Cosinus-Ähnlichkeit).
- **Workflow**:
  1. Filterung nach einem ausgewählten PDF.
  2. Indexierung der Embeddings.
  3. Abfrage mit Query-Embedding und Rückgabe der Top-`k`-Treffer.

### 3. **Cohere-Integration**
- **Prompt-Engineering**: Kontextuelle Anweisungen zur Beantwortung folgender Nutzerfragen:
   - What is the research question of the paper?
   - What is the objective of the paper
   - What is the main contribution of the paper?

- **Rate Limiting**: Begrenzung auf 10 Anfragen/Minute zur Vermeidung von API-Überlastung.
---
### 🧠 **Verwendetes LLM: Command-R-Plus-08-2024**
---
Das Modell **Command-R-Plus-08-2024** von Cohere ist ein leistungsstarkes Large Language Model (LLM), das speziell für **Retrieval-Augmented Generation (RAG)**-Anwendungen entwickelt wurde. Es kombiniert fortschrittliche Textgenerierungsfähigkeiten mit effizienter Kontextverarbeitung und ist ideal für akademische und technische Anwendungen geeignet. Dank großem Kontextfenster von bis zu **128.000 Tokens** pro Anfrage unterstützt es die Vearbeitung langer Dokumente (z.B. akademische Paper).

## 📊 Analyse der Daten
Die gesammelten Daten werden in `analysis.py` verarbeitet. Die wichtigsten Funktionen sind:
- `total_publications()`: Anzahl der Publikationen pro Jahr berechnen.
- `compute_publication_stats()`: Häufigkeit von Publikationstypen analysieren.
- `compute_journal_stats()`: Verteilung der Journals auswerten.
- `save_results()`: Ergebnisse als JSON speichern.

## 🧪 Tests
Um sicherzustellen, dass die Kernfunktionen korrekt arbeiten, sind Unit-Tests in `tests.py` definiert. Die Tests lassen sich mit folgendem Befehl ausführen:

```bash
python -m unittest tests.py
```

## 📌 Beispielergebnisse
Nach einer erfolgreichen Recherche werden die Ergebnisse gespeichert:
```
data/
├── literature_search_metadata_YYYYMMDD_HHMMSS.json
├── literature_search_results_YYYYMMDD_HHMMSS.json
```

Diese enthalten:
- **Metadaten der Suche**
- **Extrahierte Informationen aus den Publikationen**
- **KI-gestützte Analyse (Forschungsfrage, Ziel, Beitrag)**

## ⚠️  Hinweis zu API-Rate Limits
Die **Semantic Scholar API** hat eine **Rate Limit-Beschränkung**. Falls zu viele Anfragen in kurzer Zeit gesendet werden, kann die API mit **HTTP 429 (Too Many Requests)** antworten.  

Falls das Skript `429`-Fehler meldet, wird automatisch eine Pause von **10 Sekunden** eingelegt, bevor eine erneute Anfrage gesendet wird.

Weitere Informationen zu den API-Limits findest du in der [API-Dokumentation](https://www.semanticscholar.org/product/api).

## 📢 Credits & Quellen
- Publication API: [Semantic Scholar API](https://api.semanticscholar.org/)
- LLM-Anbieter: [Cohere](https://cohere.ai/)
- Quellcode der RAG-Suchmethode: [RAG_for_papers](https://github.com/ArtashesMezhlumyan/RAG_for_papers)
- zugehöriger Bericht:  [Building a Retrieval-Augmented Generation (RAG) System for Academic
Papers](https://cse.aua.am/files/2024/05/Building-a-Retrieval-Augmented-Generation-RAG-System-for-Academic-Papers.pdf)

