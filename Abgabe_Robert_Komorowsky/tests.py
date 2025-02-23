import unittest
from unittest.mock import patch
from research import build_query, search_semantic_scholar
from extraction import extract_metadata, process_papers
from analysis import total_publications, compute_publication_stats, compute_journal_stats

dummy_qa_pipeline = lambda question, context: "dummy answer for " + question

class TestResearchModule(unittest.TestCase):
    def test_build_query(self):
        """
        Testet die Funktion build_query mit verschiedenen Eingaben.
        """
        query = build_query(["term1", "term2"], or_terms=["term3"], not_terms=["term4"])
        expected = '("term1") AND ("term2") OR ("term3") NOT ("term4")'
        self.assertEqual(query, expected)

    @patch("research.requests.get")
    def test_search_semantic_scholar_empty(self, mock_get):
        """
        Mock-Funktion für search_semantic_scholar, um externe API-Aufrufe zu vermeiden.
        """
        class DummyResponse:
            def __init__(self, json_data, status_code):
                self._json = json_data
                self.status_code = status_code
            def json(self):
                return self._json

        dummy_json = {"data": []}
        mock_get.return_value = DummyResponse(dummy_json, 200)

        query = build_query("unbekannterSuchbegriff12345")
        results = search_semantic_scholar(query, limit=2)
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 0)

class TestExtractionModule(unittest.TestCase):
    def test_extract_metadata(self):
        """
        Testet die Funktion extract_metadata mit einem Beispielpaper.
        """
        paper = {
            "title": "Test Paper",
            "authors": [{"name": "John Doe"}],
            "externalIds": {"DOI": "10.1234/test"},
            "abstract": "Test abstract"
        }
        metadata = extract_metadata(paper)
        self.assertEqual(metadata["Title"], "Test Paper")
        self.assertEqual(metadata["Authors"], "John Doe")
        self.assertEqual(metadata["DOI"], "10.1234/test")
    
    @patch("extraction.os.path.exists", lambda path: False)
    @patch("extraction.os.remove", lambda path: None)
    @patch("extraction.download_pdfs", lambda urls, titles: None)
    @patch("extraction.vectorising_pdfs", lambda: None)
    @patch("extraction.query_to_cohere", new=dummy_qa_pipeline)
    def test_process_papers_with_abstract(self):
        """
        Testet die Funktion process_papers mit einem Beispiel-Paper, das kein PDF besitzt
        """
        sample_paper = {
            "title": "Sample Paper",
            "authors": [{"name": "John Doe"}],
            "year": 2022,
            "abstract": "This is an abstract of the sample paper.",
            "openAccessPdf": None,
            "citationCount": 10,
            "referenceCount": 5,
            "isOpenAccess": True,
            "externalIds": {"DOI": "10.1234/sample"},
            "publicationTypes": ["JournalArticle"],
            "journal": {"name": "Sample Journal"},
            "tldr": "TLDR text"
        }
        processed = process_papers([sample_paper])
        paper_proc = processed[0]
        self.assertEqual(paper_proc["Abstract"], "This is an abstract of the sample paper.")
        self.assertEqual(paper_proc["AI_analysis"]["Research Question"],
                         "dummy answer for What is the research question of the paper?")
        self.assertEqual(paper_proc["AI_analysis"]["Objective"],
                         "dummy answer for What is the objective of the paper?")
        self.assertEqual(paper_proc["AI_analysis"]["Contribution"],
                         "dummy answer for What is the main contribution of the paper?")

class TestAnalysisModule(unittest.TestCase):
    def test_total_publications(self):
        """
        Testet die Funktion total_publications mit einer Liste von Beispiel-Publikationen.
        """
        processed_data = [
            {"Year": 2024},
            {"Year": 2023},
            {"Year": 2024},
            {"Year": "N/A"}
        ]
        analysis = total_publications(processed_data)
        self.assertEqual(analysis["total"], 4)
        self.assertEqual(analysis["by_year"][2024], 2)
        self.assertEqual(analysis["by_year"][2023], 1)

    def test_compute_publication_stats(self):
        """
        Testet die Funktion compute_publication_stats mit einer Liste von Publikationen.
        """
        processed_data = [
            {"PublicationTypes": "JournalArticle"},
            {"PublicationTypes": "ConferencePaper, JournalArticle"},
            {"PublicationTypes": "Review, JournalArticle"}
        ]
        stats = compute_publication_stats(processed_data)
        self.assertIn("JournalArticle", stats)
        self.assertGreaterEqual(stats["JournalArticle"], 3)
        self.assertIn("ConferencePaper", stats)
    
    def test_compute_journal_stats(self):
        """
        Testet die Funktion compute_journal_stats mit einer Liste von Journals.
        """
        processed_data = [
            {"Journal": "Nature"},
            {"Journal": "Science"},
            {"Journal": "Nature"},
            {"Journal": "N/A"}
        ]
        stats = compute_journal_stats(processed_data)
        self.assertEqual(stats["Nature"], 2)
        self.assertEqual(stats["Science"], 1)

if __name__ == "__main__":
    unittest.main()
