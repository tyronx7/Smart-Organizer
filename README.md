# 📁 Smart-Organizer

![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![Typer](https://img.shields.io/badge/CLI-Typer-2e7d32.svg)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)

**Smart-Organizer** es una herramienta de línea de comandos (CLI) escrita en Python que organiza automáticamente los archivos de cualquier carpeta en subcarpetas según su tipo (Imágenes, Documentos, Videos, Audio, Código, Comprimidos, Ejecutables, etc.).

Ideal para poner en orden esa carpeta de `Descargas` que lleva meses acumulando caos.

## ✨ Características

- 🗂️ **Clasificación automática** por extensión en categorías claras.
- 🔍 **Modo `--dry-run`**: previsualiza los cambios sin mover ni un solo archivo.
- 🛡️ **Manejo robusto de errores**: rutas inexistentes, rutas inválidas o permisos denegados no rompen la ejecución.
- 🎨 **Salida enriquecida** con tablas y colores gracias a [Rich](https://github.com/Textualize/rich).
- 🚫 **No toca subcarpetas existentes**: solo organiza archivos sueltos en el nivel superior.
- 🙈 **Respeta archivos ocultos**: cualquier archivo cuyo nombre empiece con `.` (`.env`, `.gitignore`, `.config.json`, etc.) se deja intacto, ya que suele ser configuración y no "desorden" para clasificar.
- 🔁 **Sin sobrescrituras**: si ya existe un archivo con el mismo nombre en el destino, se renombra automáticamente (`archivo (1).jpg`).
- ✅ **Cubierto por pruebas unitarias** con `pytest`.

## 📦 Categorías soportadas

| Categoría     | Extensiones (ejemplos)                              |
|---------------|------------------------------------------------------|
| Imagenes      | `.jpg` `.png` `.gif` `.svg` `.webp` `.heic`           |
| Documentos    | `.pdf` `.docx` `.xlsx` `.pptx` `.csv` `.md` `.txt`    |
| Videos        | `.mp4` `.avi` `.mkv` `.mov` `.webm`                   |
| Audio         | `.mp3` `.wav` `.flac` `.ogg` `.m4a`                   |
| Comprimidos   | `.zip` `.rar` `.7z` `.tar` `.gz`                      |
| Codigo        | `.py` `.js` `.ts` `.java` `.html` `.css` `.json`      |
| Ejecutables   | `.exe` `.msi` `.apk` `.bat`                           |
| Otros         | Cualquier extensión no reconocida                     |

## 🚀 Instalación

### Requisitos previos

- Python 3.9 o superior
- pip

### Pasos

1. Clona el repositorio:

   ```bash
   git clone https://github.com/tu-usuario/smart-organizer.git
   cd smart-organizer
   ```

2. Crea y activa un entorno virtual:

   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # Linux / macOS
   source venv/bin/activate
   ```

3. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

## 🖥️ Uso

Ejecuta el comando `organize` pasando la ruta de la carpeta que quieres ordenar:

```bash
python -m src.main organize "C:\Users\tu_usuario\Downloads"
```

### Vista previa sin mover archivos (`--dry-run`)

```bash
python -m src.main organize "C:\Users\tu_usuario\Downloads" --dry-run
```

### Ejemplo de salida

```
              Archivos organizados en Downloads
+-------------+-------------------+
| Categoria   | Archivos movidos  |
+-------------+-------------------+
| Imagenes    | 12                |
| Documentos  | 5                 |
| Videos      | 2                 |
| Codigo      | 3                 |
+-------------+-------------------+
Listo! 22 archivo(s) organizados correctamente.
```

### Ver la ayuda

```bash
python -m src.main organize --help
```

## 🛡️ Robustez y casos límite

Smart-Organizer fue auditado explícitamente contra los siguientes escenarios:

| Escenario | Comportamiento |
|-----------|-----------------|
| Ruta inexistente | Muestra error claro y termina con código de salida `1`, sin excepción sin capturar. |
| Ruta que no es un directorio | Muestra error claro y termina con código de salida `1`. |
| Archivos sin extensión (`LEEME`, `Makefile`) | Se clasifican en la categoría `Otros`. |
| Archivos ocultos (`.env`, `.gitignore`, `.config.json`) | Se omiten y no se mueven (ver conteo de "omitidos" en el resumen). |
| Sin permisos para mover un archivo puntual | Se registra como error y se continúa con el resto de archivos (no se aborta todo el proceso). |
| Nombre de archivo repetido en el destino | Se renombra automáticamente en vez de sobrescribir. |

## 🧪 Testing

El proyecto incluye una suite de pruebas unitarias con `pytest` que cubre:

- Clasificación correcta por categoría.
- Manejo de extensiones desconocidas (`Otros`).
- Rutas inexistentes o inválidas.
- Modo `--dry-run`.
- Colisión de nombres de archivo en el destino.
- Comportamiento del CLI (Typer `CliRunner`).

Para ejecutar las pruebas:

```bash
pytest -v
```

## 📂 Estructura del proyecto

```
smart-organizer/
├── src/
│   ├── __init__.py
│   ├── main.py          # CLI (Typer) y presentación (Rich)
│   └── organizer.py     # Lógica de negocio: clasificación y movimiento de archivos
├── tests/
│   ├── __init__.py
│   └── test_organizer.py
├── requirements.txt
├── .gitignore
└── README.md
```

## 🛠️ Tecnologías utilizadas

- [Typer](https://typer.tiangolo.com/) — Construcción de la interfaz de línea de comandos.
- [Rich](https://rich.readthedocs.io/) — Salida de terminal con colores y tablas.
- [Pytest](https://docs.pytest.org/) — Framework de pruebas unitarias.

## 📄 Licencia

Este proyecto está disponible bajo la licencia MIT. Consultá el archivo [`LICENSE`](./LICENSE) para más detalles.
