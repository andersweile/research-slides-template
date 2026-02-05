"""Add figures to the slide deck."""

import shutil
from datetime import date
from pathlib import Path

import click
import yaml


def load_registry(path: Path = Path("slides.yaml")) -> dict:
    """Load the slides registry."""
    with open(path) as f:
        return yaml.safe_load(f)


def save_registry(data: dict, path: Path = Path("slides.yaml")) -> None:
    """Save the slides registry."""
    with open(path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)


def infer_topic_from_path(figure_path: Path) -> str | None:
    """Infer topic from the figure path (e.g., figures/data_exploration/plot.png -> data_exploration)."""
    parts = figure_path.parts
    if "figures" in parts:
        fig_idx = parts.index("figures")
        if fig_idx + 1 < len(parts) - 1:
            return parts[fig_idx + 1]
    return None


def infer_title_from_filename(figure_path: Path) -> str:
    """Convert filename to title (e.g., user_distribution.png -> User Distribution)."""
    stem = figure_path.stem
    words = stem.replace("_", " ").replace("-", " ").split()
    return " ".join(word.capitalize() for word in words)


def generate_slide_id(title: str, created: str) -> str:
    """Generate a unique slide ID from date and title."""
    slug = title.lower().replace(" ", "_")
    slug = "".join(c for c in slug if c.isalnum() or c == "_")
    return created + "_" + slug


def add_figure(
    figure_path: str,
    topic: str | None = None,
    title: str | None = None,
    caption: str = "",
    notes: str = "",
    tags: list[str] | None = None,
    copy_file: bool = False,
) -> None:
    """Add a figure to the slide deck registry."""
    tags = tags or []
    source_path = Path(figure_path)
    registry = load_registry()

    # Get valid topic IDs
    valid_topics = {t["id"] for t in registry["topics"]}

    # Infer topic if not provided
    if topic is None:
        topic = infer_topic_from_path(source_path)
        if topic is None:
            click.echo("Error: Could not infer topic from path. Please specify --topic.", err=True)
            click.echo("Valid topics: " + ", ".join(valid_topics), err=True)
            raise SystemExit(1)

    # Validate topic
    if topic not in valid_topics:
        click.echo("Error: Unknown topic '" + topic + "'.", err=True)
        click.echo("Valid topics: " + ", ".join(valid_topics), err=True)
        raise SystemExit(1)

    # Infer title if not provided
    if title is None:
        title = infer_title_from_filename(source_path)

    # Handle file copying
    if copy_file:
        dest_dir = Path("figures") / topic
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / source_path.name
        shutil.copy2(source_path, dest_path)
        figure_rel_path = str(dest_path)
        click.echo("Copied " + str(source_path) + " -> " + str(dest_path))
    else:
        figure_rel_path = str(source_path)

    # Generate slide ID and metadata
    created = date.today().isoformat()
    slide_id = generate_slide_id(title, created)

    # Check for duplicate ID
    existing_ids = {s["id"] for s in registry.get("slides", [])}
    if slide_id in existing_ids:
        # Append a counter to make unique
        counter = 2
        while slide_id + "_" + str(counter) in existing_ids:
            counter += 1
        slide_id = slide_id + "_" + str(counter)

    # Create slide entry
    slide_entry = {
        "id": slide_id,
        "topic": topic,
        "title": title,
        "caption": caption,
        "notes": notes,
        "figure": figure_rel_path,
        "created": created,
        "tags": tags,
    }

    # Add to registry
    if "slides" not in registry:
        registry["slides"] = []
    registry["slides"].append(slide_entry)

    save_registry(registry)

    click.echo("Added slide: " + title)
    click.echo("  ID: " + slide_id)
    click.echo("  Topic: " + topic)
    click.echo("  Figure: " + figure_rel_path)
    if caption:
        click.echo("  Caption: " + caption)
    click.echo("  Created: " + created)
    if tags:
        click.echo("  Tags: " + ", ".join(tags))
    click.echo("\nRun 'slidedeck build' to regenerate QMD files.")
