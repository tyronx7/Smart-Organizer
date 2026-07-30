"""Core logic for organizing files into category subfolders by extension."""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path

# Maps each category folder name to the set of file extensions that belong to it.
CATEGORY_MAP: dict[str, set[str]] = {
    "Imagenes": {
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".tiff", ".ico", ".heic",
    },
    "Documentos": {
        ".pdf", ".doc", ".docx", ".txt", ".xlsx", ".xls", ".ppt", ".pptx",
        ".csv", ".odt", ".ods", ".odp", ".md", ".rtf",
    },
    "Videos": {
        ".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v",
    },
    "Audio": {
        ".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma",
    },
    "Comprimidos": {
        ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz",
    },
    "Codigo": {
        ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".c", ".cpp", ".h", ".hpp",
        ".html", ".css", ".json", ".xml", ".sh", ".php", ".go", ".rs", ".rb", ".sql",
        ".yaml", ".yml", ".ipynb",
    },
    "Ejecutables": {
        ".exe", ".msi", ".apk", ".bat", ".sh_exec", ".appimage",
    },
}

OTHERS_CATEGORY = "Otros"


def _category_for_extension(extension: str) -> str:
    """Return the destination category folder name for a given file extension."""
    extension = extension.lower()
    for category, extensions in CATEGORY_MAP.items():
        if extension in extensions:
            return category
    return OTHERS_CATEGORY


def _unique_destination(destination_dir: Path, filename: str) -> Path:
    """Avoid overwriting existing files by appending a numeric suffix on collision."""
    destination = destination_dir / filename
    if not destination.exists():
        return destination

    stem, suffix = Path(filename).stem, Path(filename).suffix
    counter = 1
    while True:
        candidate = destination_dir / f"{stem} ({counter}){suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


@dataclass
class OrganizeResult:
    """Summary of an organize operation, used for CLI reporting and tests."""

    moved: dict[str, int] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    skipped: int = 0
    dry_run: bool = False

    @property
    def total_moved(self) -> int:
        return sum(self.moved.values())


def organize_directory(target_path: str | Path, dry_run: bool = False) -> OrganizeResult:
    """Organize files in ``target_path`` into category subfolders by extension.

    Only top-level files are processed; existing subdirectories are left untouched.
    Raises FileNotFoundError / NotADirectoryError for an invalid target so the
    CLI layer can present a clear, user-facing error message.
    """
    path = Path(target_path).expanduser().resolve()

    if not path.exists():
        raise FileNotFoundError(f"La ruta no existe: {path}")
    if not path.is_dir():
        raise NotADirectoryError(f"La ruta no es un directorio: {path}")

    result = OrganizeResult(dry_run=dry_run)

    entries = sorted(p for p in path.iterdir() if p.is_file())

    for file_path in entries:
        if file_path.name.startswith("."):
            # Dotfiles (.env, .gitignore, ...) are usually configuration, not
            # clutter to sort - leave them where the user put them.
            result.skipped += 1
            continue

        category = _category_for_extension(file_path.suffix)
        destination_dir = path / category

        try:
            if not dry_run:
                destination_dir.mkdir(exist_ok=True)
                destination = _unique_destination(destination_dir, file_path.name)
                shutil.move(str(file_path), str(destination))
            result.moved[category] = result.moved.get(category, 0) + 1
        except PermissionError:
            result.errors.append(f"Permiso denegado al mover: {file_path.name}")
        except OSError as exc:
            result.errors.append(f"Error al mover {file_path.name}: {exc}")

    return result
