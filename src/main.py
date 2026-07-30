"""Smart-Organizer CLI entrypoint."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from src.organizer import OrganizeResult, organize_directory

app = typer.Typer(
    name="smart-organizer",
    help="Organiza automaticamente los archivos de una carpeta en subcarpetas por tipo.",
    add_completion=False,
)
console = Console()


@app.callback()
def callback() -> None:
    """Smart-Organizer: organiza tus archivos automaticamente por tipo."""


def _print_summary(result: OrganizeResult, target: str) -> None:
    if result.total_moved == 0 and not result.errors and not result.skipped:
        console.print(f"[yellow]No se encontraron archivos para organizar en '{target}'.[/yellow]")
        return

    verb = "se organizarian" if result.dry_run else "organizados"
    table = Table(title=f"Archivos {verb} en {target}")
    table.add_column("Categoria", style="cyan", no_wrap=True)
    table.add_column("Archivos movidos", justify="right", style="green")

    for category, count in sorted(result.moved.items()):
        table.add_row(category, str(count))

    console.print(table)

    if result.dry_run:
        console.print(f"[blue]Vista previa (dry-run): {result.total_moved} archivo(s) se moverian.[/blue]")
    else:
        console.print(f"[bold green]Listo! {result.total_moved} archivo(s) organizados correctamente.[/bold green]")

    if result.skipped:
        console.print(
            f"[dim]{result.skipped} archivo(s) oculto(s) omitidos (no se tocan por seguridad).[/dim]"
        )

    if result.errors:
        console.print("[bold red]Se encontraron errores:[/bold red]")
        for error in result.errors:
            console.print(f"  [red]- {error}[/red]")


@app.command()
def organize(
    path: str = typer.Argument(..., help="Ruta del directorio a organizar."),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Muestra que se haria sin mover archivos realmente."
    ),
) -> None:
    """Organiza los archivos de PATH en subcarpetas segun su extension."""
    try:
        result = organize_directory(path, dry_run=dry_run)
    except FileNotFoundError:
        console.print(f"[bold red]Error:[/bold red] La ruta '{path}' no existe.")
        raise typer.Exit(code=1)
    except NotADirectoryError:
        console.print(f"[bold red]Error:[/bold red] '{path}' no es un directorio.")
        raise typer.Exit(code=1)
    except PermissionError:
        console.print(f"[bold red]Error:[/bold red] Permiso denegado para acceder a '{path}'.")
        raise typer.Exit(code=1)

    _print_summary(result, path)

    if result.errors:
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
