"""
Extraccion de texto de los PDFs de insumo (demanda, contestacion, ampliacion,
fijacion de puntos controvertidos, medios probatorios, etc.)

No asume un orden ni una cantidad fija de archivos: procesa todos los PDF que
encuentre en la carpeta de entrada. La clasificacion final de "que es cada
documento" la hace el modelo de lenguaje a partir del contenido, pero aqui se
agrega una pista (hint) por nombre de archivo cuando es obvia, para ayudar.
"""
import pathlib
import re

import pdfplumber

# Palabras clave -> pista de tipo de documento (solo orientativa, no vinculante)
HINTS = [
    (r"amplia", "posible AMPLIACION DE DEMANDA"),
    (r"contesta", "posible CONTESTACION DE DEMANDA"),
    (r"demanda", "posible DEMANDA"),
    (r"fijaci|controvert|saneamiento", "posible RESOLUCION DE FIJACION DE PUNTOS CONTROVERTIDOS"),
    (r"prueba|probator", "posible MEDIOS PROBATORIOS / EXPEDIENTE ADMINISTRATIVO"),
    (r"modelo|plantilla|formato", "documento de REFERENCIA DE FORMATO (no es parte del caso)"),
]


def guess_hint(filename: str) -> str:
    name = filename.lower()
    for pattern, hint in HINTS:
        if re.search(pattern, name):
            return hint
    return "tipo no identificado por nombre de archivo; identificar por contenido"


def extract_pdf_text(path: pathlib.Path, max_chars: int = 60_000) -> str:
    """Extrae el texto de un PDF. Si una pagina no tiene capa de texto
    (posible escaneo), lo señala en vez de fallar silenciosamente."""
    chunks = []
    empty_pages = 0
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            if not text.strip():
                empty_pages += 1
                continue
            chunks.append(f"[Pagina {i}]\n{text}")
    full_text = "\n\n".join(chunks)
    if empty_pages:
        full_text += (
            f"\n\n[AVISO: {empty_pages} pagina(s) de este PDF no tenian texto "
            "extraible; probablemente son imagenes escaneadas. Si falta "
            "informacion importante, aplica OCR antes de volver a correr "
            "el pipeline.]"
        )
    if len(full_text) > max_chars:
        full_text = full_text[:max_chars] + "\n\n[...TEXTO TRUNCADO POR LONGITUD...]"
    return full_text


def load_documents(input_dir: str) -> list[dict]:
    """Devuelve una lista de {archivo, hint, texto} para cada PDF en input_dir."""
    folder = pathlib.Path(input_dir)
    pdfs = sorted(folder.glob("*.pdf"))
    if not pdfs:
        raise FileNotFoundError(f"No se encontraron archivos .pdf en {input_dir}")

    documentos = []
    for pdf_path in pdfs:
        texto = extract_pdf_text(pdf_path)
        documentos.append({
            "archivo": pdf_path.name,
            "hint": guess_hint(pdf_path.name),
            "texto": texto,
        })
    return documentos
