"""Unit tests for Smart-Organizer's core logic and CLI."""

import shutil

import pytest
from typer.testing import CliRunner

import src.main as main_module
from src.main import app
from src.organizer import organize_directory

runner = CliRunner()


def _touch(path, name):
    (path / name).write_text("contenido de prueba")


@pytest.fixture
def messy_dir(tmp_path):
    """A temporary directory populated with fake files of various types."""
    _touch(tmp_path, "foto.jpg")
    _touch(tmp_path, "documento.pdf")
    _touch(tmp_path, "pelicula.mp4")
    _touch(tmp_path, "cancion.mp3")
    _touch(tmp_path, "script.py")
    _touch(tmp_path, "archivo.xyz123")  # unknown extension -> "Otros"
    (tmp_path / "ya_organizado").mkdir()  # existing subfolder, must be ignored
    return tmp_path


class TestOrganizeDirectory:
    def test_moves_files_into_correct_categories(self, messy_dir):
        result = organize_directory(messy_dir)

        assert (messy_dir / "Imagenes" / "foto.jpg").exists()
        assert (messy_dir / "Documentos" / "documento.pdf").exists()
        assert (messy_dir / "Videos" / "pelicula.mp4").exists()
        assert (messy_dir / "Audio" / "cancion.mp3").exists()
        assert (messy_dir / "Codigo" / "script.py").exists()
        assert result.total_moved == 6
        assert not result.errors

    def test_unknown_extension_goes_to_otros(self, messy_dir):
        organize_directory(messy_dir)
        assert (messy_dir / "Otros" / "archivo.xyz123").exists()

    def test_ignores_existing_subdirectories(self, messy_dir):
        organize_directory(messy_dir)
        # The pre-existing folder must remain untouched, not treated as a file.
        assert (messy_dir / "ya_organizado").is_dir()
        assert not (messy_dir / "Otros" / "ya_organizado").exists()

    def test_nonexistent_path_raises_filenotfounderror(self, tmp_path):
        fake_path = tmp_path / "no_existe"
        with pytest.raises(FileNotFoundError):
            organize_directory(fake_path)

    def test_path_is_file_raises_notadirectoryerror(self, tmp_path):
        file_path = tmp_path / "soy_un_archivo.txt"
        file_path.write_text("hola")
        with pytest.raises(NotADirectoryError):
            organize_directory(file_path)

    def test_dry_run_does_not_move_files(self, messy_dir):
        result = organize_directory(messy_dir, dry_run=True)

        assert result.dry_run is True
        assert result.total_moved == 6
        # No category folders should have been created on disk.
        assert not (messy_dir / "Imagenes").exists()
        assert (messy_dir / "foto.jpg").exists()

    def test_handles_filename_collision(self, tmp_path):
        _touch(tmp_path, "foto.jpg")
        (tmp_path / "Imagenes").mkdir()
        (tmp_path / "Imagenes" / "foto.jpg").write_text("ya existente")

        result = organize_directory(tmp_path)

        assert (tmp_path / "Imagenes" / "foto.jpg").read_text() == "ya existente"
        assert (tmp_path / "Imagenes" / "foto (1).jpg").exists()
        assert result.total_moved == 1

    def test_empty_directory_moves_nothing(self, tmp_path):
        result = organize_directory(tmp_path)
        assert result.total_moved == 0
        assert not result.errors

    def test_extensionless_files_go_to_otros(self, tmp_path):
        _touch(tmp_path, "LEEME")
        _touch(tmp_path, "Makefile")

        result = organize_directory(tmp_path)

        assert (tmp_path / "Otros" / "LEEME").exists()
        assert (tmp_path / "Otros" / "Makefile").exists()
        assert result.total_moved == 2

    def test_hidden_dotfiles_are_skipped_not_moved(self, tmp_path):
        _touch(tmp_path, ".env")
        _touch(tmp_path, ".config.json")
        _touch(tmp_path, "foto.jpg")

        result = organize_directory(tmp_path)

        # Dotfiles stay exactly where they were - never touched.
        assert (tmp_path / ".env").exists()
        assert (tmp_path / ".config.json").exists()
        assert result.skipped == 2
        assert result.total_moved == 1
        assert not (tmp_path / "Otros").exists()

    def test_permission_error_on_one_file_does_not_abort_others(self, tmp_path, monkeypatch):
        _touch(tmp_path, "foto.jpg")
        _touch(tmp_path, "documento.pdf")

        real_move = shutil.move

        def flaky_move(src, dst):
            if "foto.jpg" in src:
                raise PermissionError("Acceso denegado (simulado)")
            return real_move(src, dst)

        monkeypatch.setattr(shutil, "move", flaky_move)

        result = organize_directory(tmp_path)

        assert (tmp_path / "Documentos" / "documento.pdf").exists()
        assert (tmp_path / "foto.jpg").exists()  # never moved due to the error
        assert result.total_moved == 1
        assert len(result.errors) == 1
        assert "foto.jpg" in result.errors[0]


class TestCli:
    def test_cli_organize_success(self, messy_dir):
        exit_result = runner.invoke(app, ["organize", str(messy_dir)])
        assert exit_result.exit_code == 0
        assert (messy_dir / "Imagenes" / "foto.jpg").exists()

    def test_cli_organize_nonexistent_path(self, tmp_path):
        fake_path = tmp_path / "no_existe"
        exit_result = runner.invoke(app, ["organize", str(fake_path)])
        assert exit_result.exit_code == 1

    def test_cli_organize_dry_run_flag(self, messy_dir):
        exit_result = runner.invoke(app, ["organize", str(messy_dir), "--dry-run"])
        assert exit_result.exit_code == 0
        assert not (messy_dir / "Imagenes").exists()

    def test_cli_reports_permission_error_on_directory_access(self, tmp_path, monkeypatch):
        def raise_permission_error(*_args, **_kwargs):
            raise PermissionError("Acceso denegado (simulado)")

        monkeypatch.setattr(main_module, "organize_directory", raise_permission_error)

        exit_result = runner.invoke(app, ["organize", str(tmp_path)])

        assert exit_result.exit_code == 1
        assert "Permiso denegado" in exit_result.output

    def test_cli_reports_skipped_hidden_files(self, tmp_path):
        _touch(tmp_path, ".env")
        _touch(tmp_path, "foto.jpg")

        exit_result = runner.invoke(app, ["organize", str(tmp_path)])

        assert exit_result.exit_code == 0
        assert "omitidos" in exit_result.output
        assert (tmp_path / ".env").exists()
