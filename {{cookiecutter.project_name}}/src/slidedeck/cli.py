"""CLI interface for the slidedeck tool."""

import click

from slidedeck.add import add_figure
from slidedeck.build import build_slides
from slidedeck.history import show_history, generate_comparison


@click.group()
def cli():
    """Manage research slide decks."""
    pass


@cli.command()
@click.argument("figure_path", type=click.Path(exists=True))
@click.option("--topic", "-t", help="Topic ID (inferred from path if not provided)")
@click.option("--title", "-T", help="Slide title (inferred from filename if not provided)")
@click.option("--caption", "-c", default="", help="Figure caption (appears below the figure)")
@click.option("--notes", "-n", default="", help="Speaker notes (not visible on slides)")
@click.option("--tags", help="Comma-separated tags")
@click.option("--copy", is_flag=True, help="Copy figure to figures/ directory")
def add(figure_path: str, topic: str | None, title: str | None, caption: str, notes: str, tags: str | None, copy: bool):
    """Add a new figure to the slide deck.

    FIGURE_PATH is the path to the figure image file.

    Examples:

        slidedeck add figures/data_exploration/my_plot.png

        slidedeck add my_plot.png --topic modeling --title "Results" --copy

        slidedeck add figures/results/final.png -t results -T "Final Results" -c "Model performance over time"
    """
    tag_list = [t.strip() for t in tags.split(",")] if tags else []
    add_figure(figure_path, topic=topic, title=title, caption=caption, notes=notes, tags=tag_list, copy_file=copy)


@cli.command()
@click.option("--recent-count", "-n", default=10, help="Number of recent figures to show")
def build(recent_count: int):
    """Build/regenerate all QMD files from slides.yaml."""
    build_slides(recent_count=recent_count)


@cli.command()
def preview():
    """Build and preview the slides."""
    import subprocess

    build_slides()
    click.echo("Starting Quarto preview...")
    subprocess.run(["quarto", "preview"], check=True)


@cli.command()
@click.argument("figure_path", type=click.Path(exists=True))
def history(figure_path: str):
    """View git history of a specific figure.

    FIGURE_PATH is the path to the figure image file.
    """
    show_history(figure_path)


@cli.command()
@click.argument("figure_path", type=click.Path(exists=True))
@click.option("--output", "-o", default="comparison.html", help="Output HTML file")
def compare(figure_path: str, output: str):
    """Generate comparison view of figure versions from git history.

    FIGURE_PATH is the path to the figure image file.
    """
    generate_comparison(figure_path, output)


if __name__ == "__main__":
    cli()
