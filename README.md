# Generador de proyectos de sentencia (laboral / contencioso-administrativo)

Convierte los PDF de un expediente (demanda, contestación, ampliación de
demanda, resolución de fijación de puntos controvertidos, medios
probatorios...) en un `.docx` con el formato estándar de una sentencia
peruana. No importa si son 6, 7 u 8 archivos, ni el orden.

## Versión gratuita (recomendada — sin API key, sin costo)

Usa **NotebookLM** (https://notebooklm.google.com), gratis con cualquier
cuenta de Google, para que la IA lea los PDF y redacte el contenido. Este
programa (`app.py`) solo se encarga de darle el formato correcto de Word a
esa respuesta — no llama a ninguna API ni tiene ningún costo.

### Paso 0 — una sola vez: instalar Python

Si la computadora no tiene Python: bajarlo de
https://www.python.org/downloads/ e instalarlo. **En Windows, durante la
instalación, marcar la casilla "Add python.exe to PATH"**. En Mac
normalmente ya viene instalado.

### Paso 1 — una sola vez: instalar el programa

- **Windows:** doble clic en `1_INSTALAR (una sola vez).bat`
- **Mac:** doble clic en `1_INSTALAR (una sola vez).command`
  (la primera vez, si Mac bloquea el archivo: clic derecho → Abrir → Abrir)

### Paso 2 — abrir el programa

- **Windows:** doble clic en `2_ABRIR_APP.bat`
- **Mac:** doble clic en `2_ABRIR_APP.command`

Se abre una pestaña del navegador con la aplicación. Ahí, sigue los 3 pasos
que muestra la pantalla:

1. **Sube los PDF a NotebookLM.** Entra a notebooklm.google.com, crea un
   cuaderno nuevo ("+ Crear cuaderno nuevo") y sube ahí todos los PDF del
   expediente como fuentes.
2. **Copia el texto que te muestra nuestra app** (el mismo que está en
   `PROMPT_PARA_NOTEBOOKLM.txt`) y pégalo en el chat de NotebookLM, dentro
   del cuaderno donde subiste los PDF. Espera la respuesta.
3. **Copia toda la respuesta de NotebookLM** (debería ser un bloque que
   empieza con `{` y termina con `}`) y pégala en el cuadro de nuestra app.
   Dale clic a "Generar Word" y descarga el archivo.

Para cerrar el programa, cierra la ventana negra que quedó abierta detrás
del navegador.

### Si NotebookLM no responde solo con el JSON

A veces agrega una frase antes o después ("Aquí tienes el JSON:", etc.) o
lo envuelve en un bloque de código con ```. La app ya intenta limpiar eso
automáticamente; si aun así da error, revisa que hayas copiado la respuesta
**completa**, desde la primera `{` hasta la última `}`.

### Límites de NotebookLM a tener en cuenta

La cuenta gratuita de Google permite varios cuadernos y hasta 50 fuentes
por cuaderno, así que un expediente de 6 a 8 PDF entra sin problema. Si
algún PDF es un escaneo sin texto (foto), NotebookLM puede tener problemas
para leerlo igual que cualquier otra herramienta — en ese caso hay que
pasarlo antes por un OCR.

---

## Versión avanzada (opcional): automática con API de pago

Si en algún momento se prefiere que todo el proceso sea 100% automático
(sin pasar por NotebookLM a mano), existe también `generar_sentencia.py`,
que hace exactamente lo mismo pero llamando directamente a una API de
Claude (Anthropic). Esto sí tiene un costo pequeño por cada sentencia
generada y requiere una API key. Instrucciones:

```bash
pip install pdfplumber anthropic  # además de lo que ya instalaste
export ANTHROPIC_API_KEY="tu-api-key-aqui"

python generar_sentencia.py --input caso_2026/ --output Proyecto_Sentencia.docx
```

## Cómo funciona por dentro

- `PROMPT_PARA_NOTEBOOKLM.txt`: las instrucciones que le decimos a la IA —
  qué hacer con los documentos, qué formato de sentencia seguir, y que NO
  invente datos que no estén en los PDF (si falta algo, debe escribir
  `[NO CONSTA EN LOS DOCUMENTOS PROPORCIONADOS]`).
- `src/render.py`: toma el JSON (venga de NotebookLM copiado a mano, o de
  la API en la versión avanzada) y arma el `.docx` con `python-docx`,
  replicando el formato típico de una sentencia (encabezado del juzgado,
  negritas/subrayado en los títulos de cada considerando, numeración...).
- `app.py`: la pantalla que guía los 3 pasos y llama a `render.py`.
- `src/extract.py` y `src/llm.py`: solo los usa la versión avanzada
  (`generar_sentencia.py`) para leer los PDF y llamar a la API
  automáticamente.

## Limitaciones a tener en cuenta

- **Esto genera un borrador de trabajo, no una sentencia lista para firmar.**
  La IA solo ve los documentos que se subieron — si el expediente real
  tiene más tomos o pruebas, el proyecto no las va a considerar. Siempre
  hay que revisar la sección "NOTAS PARA REVISIÓN" al final del Word y
  cotejar contra el expediente completo.
- El nombre de archivo de los PDF no importa para nada en esta versión.
