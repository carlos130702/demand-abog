"""
Version SIN API KEY y SIN COSTO.

En vez de que este programa llame a una API de pago, tu hermana usa
NotebookLM (gratis, https://notebooklm.google.com, solo necesita una
cuenta de Google) para que la IA lea los PDF y redacte el proyecto de
sentencia. Este programa solo se encarga de tomar esa respuesta y darle
el formato correcto de Word -- exactamente el mismo formato que la version
automatica, hecho con el mismo motor (src/render.py).

Flujo (ver tambien README.md):
  1. Crear un cuaderno nuevo en NotebookLM y subir ahi los PDF del caso.
  2. Copiar el contenido de PROMPT_PARA_NOTEBOOKLM.txt en el chat de
     NotebookLM (boton "Copiar" mas abajo).
  3. Copiar la respuesta completa que da NotebookLM (deberia ser un JSON).
  4. Pegarla en el cuadro de esta pagina y darle a "Generar Word".

    streamlit run app.py
"""
import json
import pathlib
import sys
import tempfile

import streamlit as st

sys.path.insert(0, str(pathlib.Path(__file__).parent / "src"))

from render import build_docx  # noqa: E402

NOTA_DEFAULT = (
    "Este documento es un PROYECTO generado con ayuda de IA (NotebookLM) a "
    "partir de los PDF de insumo. Debe ser revisado contra el expediente "
    "completo antes de firmarse: verificar fechas, numeros de resolucion, "
    "computo de plazos y cualquier dato marcado como "
    "'[NO CONSTA EN LOS DOCUMENTOS PROPORCIONADOS]'. Ver tambien la seccion "
    "'NOTAS PARA REVISION' al final del documento."
)

PROMPT_PATH = pathlib.Path(__file__).parent / "PROMPT_PARA_NOTEBOOKLM.txt"
PROMPT_TEXTO = PROMPT_PATH.read_text(encoding="utf-8")

st.set_page_config(page_title="Generador de Proyectos de Sentencia", layout="centered")
st.title("⚖️ Generador de Proyectos de Sentencia")
st.caption("Versión gratuita — usa NotebookLM en vez de una API de pago.")

st.markdown("### Paso 1 — Sube los PDF a NotebookLM")
st.write(
    "Entra a [notebooklm.google.com](https://notebooklm.google.com) con una "
    "cuenta de Google (es gratis), crea un cuaderno nuevo y sube ahí todos "
    "los PDF del expediente (demanda, contestación, ampliación, fijación de "
    "puntos controvertidos, medios probatorios...). No importa cuántos sean."
)

st.markdown("### Paso 2 — Copia este texto y pégalo en el chat de NotebookLM")
st.code(PROMPT_TEXTO, language=None)
st.caption("Usa el ícono de copiar que aparece arriba a la derecha del cuadro.")

st.markdown("### Paso 3 — Pega aquí la respuesta que te dio NotebookLM")
respuesta = st.text_area(
    "Respuesta de NotebookLM (debería empezar con { y terminar con })",
    height=250,
    placeholder='{\n  "encabezado": { ... },\n  "argumento_demandante": [...],\n  ...\n}',
)

generar = st.button("📄 Generar Word", type="primary", use_container_width=True)

if generar:
    if not respuesta.strip():
        st.error("Pega primero la respuesta de NotebookLM.")
        st.stop()

    texto = respuesta.strip()
    # Por si NotebookLM envolvió el JSON en un bloque de código ```...```
    if texto.startswith("```"):
        texto = texto.strip("`")
        if texto.lower().startswith("json"):
            texto = texto[4:]
    # Por si agregó texto antes/después del JSON, recorta al primer { y al último }
    inicio = texto.find("{")
    fin = texto.rfind("}")
    if inicio != -1 and fin != -1:
        texto = texto[inicio:fin + 1]

    try:
        data = json.loads(texto)
    except json.JSONDecodeError as exc:
        st.error(
            "No pude leer eso como JSON válido. Revisa que hayas copiado la "
            "respuesta completa de NotebookLM (desde la primera { hasta la "
            f"última }}). Detalle técnico: {exc}"
        )
        st.stop()

    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp_out:
        build_docx(data, tmp_out.name, nota_de_trabajo=NOTA_DEFAULT)
        docx_bytes = pathlib.Path(tmp_out.name).read_bytes()
        pathlib.Path(tmp_out.name).unlink(missing_ok=True)

    st.success("¡Proyecto de sentencia listo!")

    notas = data.get("notas_para_revision", [])
    if notas:
        st.warning("Puntos que NotebookLM marcó para tu revisión:")
        for n in notas:
            st.write(f"- {n}")

    st.download_button(
        label="⬇️ Descargar Proyecto_Sentencia.docx",
        data=docx_bytes,
        file_name="Proyecto_Sentencia.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        use_container_width=True,
    )
