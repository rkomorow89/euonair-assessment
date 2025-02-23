import os
import re
import requests
from urllib.parse import urlparse
from datetime import datetime
from typing import List

def sanitize_filename(name: str) -> str:
    """Ersetzt ungültige Zeichen in Dateinamen durch Unterstriche und kürzt lange Namen.
    
    Args:
        name (str): Der ursprüngliche Dateiname.
    
    Returns:
        str: Der bereinigte Dateiname, maximal 100 Zeichen lang.
    """
    name = re.sub(r'[<>:"/\\|?*]', '_', name) 
    return name[:100]  

def download_pdfs(urls: List[str], titles: List[str]) -> None:
    """Lädt PDFs von den übergebenen URLs herunter und speichert sie mit den zugehörigen Titeln.
    
    Erstellt einen Unterordner mit einem Zeitstempel und speichert die heruntergeladenen PDFs dort.
    
    Args:
        urls (List[str]): Eine Liste von URLs zu den PDF-Dateien.
        titles (List[str]): Eine Liste von Dateinamen für die heruntergeladenen PDFs.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  
    save_dir = os.path.join("pdf_manipulations", "pdf_db", timestamp)
    os.makedirs(save_dir, exist_ok=True)  

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    })

    for url, title in zip(urls, titles):
        try:
            parsed_url = urlparse(url)
            referer = f"{parsed_url.scheme}://{parsed_url.netloc}/"

            headers = {
                "Referer": referer
            }

            response = session.get(url, headers=headers, stream=True)
            if response.status_code == 200:
                clean_title = sanitize_filename(title)
                file_name = f"{clean_title}.pdf"
                file_path = os.path.join(save_dir, file_name)

                if os.path.exists(file_path):
                    print(f"File {file_path} already exists. Skipping...")
                    continue

                with open(file_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=1024):
                        file.write(chunk)

                print(f"Downloaded: {file_path}")
            else:
                print(f"Failed to download {url}. Status code: {response.status_code}")

        except Exception as e:
            print(f"Error downloading {url}: {e}")

# Beispielhafte Liste von URLs und Titeln
urls = [
    "https://arxiv.org/pdf/2304.09103",
    "https://journals.eanso.org/index.php/eaje/article/download/1272/1838"
]
titles = [
    "ChatGPT: Applications, Opportunities, and Threats",
    "Application of CHATGPT in civil engineering"
]

#download_pdfs(urls, titles)


