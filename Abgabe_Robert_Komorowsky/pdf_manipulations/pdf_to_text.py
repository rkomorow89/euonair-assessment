from pdf_manipulations.pdfminer.high_level import extract_text
from typing import Union
from pathlib import Path
import re

def extract_cleaned_text(path_to_pdf: Union[str, Path]) -> str:
    """
    Extrahiert und bereinigt den Text aus einer PDF-Datei, indem unerwünschte Muster entfernt werden.

    Args:
        path_to_pdf (Union[str, Path]): Der Pfad zur PDF-Datei als Zeichenkette oder Path-Objekt.

    Returns:
        str: Der bereinigte Text aus der PDF-Datei.
    """
    text = extract_text(path_to_pdf)
    patterns = [
        r'\b\d+/\d+\b',  
        r'\b[A-Za-z]+\(\d+\)',  
        r'\b\d+\^\d+\b',  
        r'=\s*[+-]?(\d+(\.\d*)?|\.\d+)',  
        r'[α-ωΑ-Ω]+',  
        r'[≈≥≤±]+',  
        r'∑|∫|∂',  
        r'\b[A-Za-z]{1,2}_?\d*[\^_]?\d+\b',  
        r'\bwhere\b',  
        r'\bFig\.\s*\d+|\bTable\s*\d+|\[\d+(-\d+)?\]',  
        r'\b[NnCcFf]\s?=\s?[A-Za-z0-9\-\+\*/\^]+',  
        r'\b\d+\s?[\+\-\*/\^]\s?\d+',  
        r'\([A-Za-z0-9\+\-\*/\^\s]+\)',  
        r'\[[A-Za-z0-9\+\-\*/\^\s]+\]',  
        r'\{[A-Za-z0-9\+\-\*/\^\s]+\}',  
        r'\b[A-Za-z]+[\_\/\^\(][A-Za-z0-9\+\-\*]+',  
        r'≈|≥|≤|±|\∑|\∫|\∂',  
        r'\balpha\b|\bbeta\b|\bgamma\b|\bdelta\b',  
        r'[α-ωΑ-Ω]',  
        r'\d+[.,]?\d*\s*(×\s*10\^\s*[\-\+]?\d+)?',  
        r'\b(?:sin|cos|tan|log|ln|exp)\b',  
        r'[A-Za-z]\s?\([\w\s,]*\)\s?=',  
        r'[A-Za-z]\s?[_\^]\s?[A-Za-z0-9]+',  
        r'\b[A-Za-z]{1,3}\b[\s-]*[\+\-\*/^]=',  
        r'\([^\)]+\)',  
        r'\b\d+\.?\d*\s*[\+\-\*/^]\s*\d+\.?\d*\b',  
        r'[A-Za-z]+[\d\+\-\*/^]+',  
        r'\b(?:sin|cos|tan|log|exp|ln)\([^\)]+\)',  
        r'\b[A-Za-z]+[_\^][A-Za-z0-9]+\b',  
        r'\b\w+\s*\=\s*[^\;]+\;',  
        r'\b\d+\s*[\+\-\*/\^]\s*\d+',  
        r'[α-ωΑ-Ω]',  
        r'\b(?:sin|cos|tan|log|ln|exp)\b\([^\)]*\)',  
        r'\b[A-Za-z]{1,2}\d*\s?[\+\-\*/\^]=\s?[A-Za-z]{1,2}\d*',  
        r'n\s?X',  
        r'[A-Za-z]+\s?\-\s?[A-Za-z]+',  
        r'\bCF\s?=\s?[^\;]+\;',  
        r'∑|∫|∂',  
        r'\([^)]+\)',  
        r'\b[A-Za-z]+\s?\*?\s?\([^\)]+\)\s?=',  
        r'A[^\s,]+,\s*QT\s*,\s*y,\s*Ω\*?\)\s*=',  
        r'\bS\s*\n[^\n]+n\s*o\s*,',  
        r'\bFi,\s*\b',  
        r'\bFg,\s*\b',  
        r'F[ig],\s*\+?\s*F[ig],\+?',  
        r'\bXi=[^\n]+\.\.\.,',  
        r'⊗',  
        r'f[¯]?[^\s]+\s*[⊗]',  
        r'µF\s*/\s*Q',  
        r'[PF]\'?[ig],\+?',  
    ]
    text = re.sub(r'\s+', ' ', text).strip()  
    return text

