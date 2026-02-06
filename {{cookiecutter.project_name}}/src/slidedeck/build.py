"""Build QMD files from the slides registry."""

from pathlib import Path

import click
import yaml


def load_registry(path: Path = Path("slides.yaml")) -> dict:
    """Load the slides registry."""
    with open(path) as f:
        return yaml.safe_load(f)


def _render_slide(slide: dict, lines: list[str]) -> None:
    """Render a single slide's content (figure and/or markdown) into lines."""
    # Figure with optional caption
    figure = slide.get("figure", "")
    if figure:
        caption = slide.get("caption", "") or slide.get("description", "")
        lines.extend([
            "![](" + figure + ")",
            "",
        ])
        if caption:
            lines.extend([
                "::: " + "{" + ".caption}",
                caption.rstrip(),
                ":::",
                "",
            ])

    # Markdown content (for text-only or mixed slides)
    content = slide.get("content", "")
    if content:
        lines.extend([
            content.rstrip(),
            "",
        ])

    # Speaker notes
    notes = slide.get("notes", "")
    if notes:
        lines.extend([
            "::: " + "{" + ".notes}",
            notes,
            ":::",
            "",
        ])


def build_slides_qmd(registry: dict) -> str:
    """Generate the main slides.qmd content."""
    title = registry.get("title", "Research Figures")
    lines = [
        "---",
        'title: "' + title + '"',
        "format:",
        "  revealjs:",
        "    theme: default",
        "    slide-number: true",
        "    fig-cap-location: bottom",
        "    margin: 0.05",
        "    scrollable: true",
        "css: styles.css",
        "---",
        "",
    ]

    slides = registry.get("slides", [])
    if not slides:
        lines.extend([
            "# Welcome",
            "",
            "No figures added yet.",
            "",
            "Run `slidedeck add` to add your first figure.",
        ])
        return "\n".join(lines)

    # Group slides by topic
    topics = {t["id"]: t for t in registry["topics"]}
    topic_order = {t["id"]: t["order"] for t in registry["topics"]}

    slides_by_topic: dict[str, list] = {}
    for slide in slides:
        topic_id = slide["topic"]
        if topic_id not in slides_by_topic:
            slides_by_topic[topic_id] = []
        slides_by_topic[topic_id].append(slide)

    # Sort topics by order
    sorted_topic_ids = sorted(slides_by_topic.keys(), key=lambda x: topic_order.get(x, 999))

    for topic_id in sorted_topic_ids:
        topic = topics.get(topic_id, {"name": topic_id.replace("_", " ").title()})
        topic_slides = slides_by_topic[topic_id]

        # Sort slides by date (newest first within topic)
        topic_slides.sort(key=lambda s: s["created"], reverse=True)

        # Topic header
        anchor = topic_id.replace("_", "-")
        lines.extend([
            "# " + topic["name"] + " " + "{" + "#" + anchor + "}",
            "",
        ])

        for slide in topic_slides:
            lines.extend([
                "## " + slide["title"] + " " + "{" + "#" + slide["id"] + "}",
                "",
            ])
            _render_slide(slide, lines)

    return "\n".join(lines)


def build_recent_qmd(registry: dict, count: int = 10) -> str:
    """Generate the recent.qmd content showing most recent figures."""
    lines = [
        "---",
        'title: "Recent Figures"',
        "format:",
        "  revealjs:",
        "    theme: default",
        "    slide-number: true",
        "    fig-cap-location: bottom",
        "css: styles.css",
        "---",
        "",
    ]

    slides = registry.get("slides", [])
    if not slides:
        lines.extend([
            "# Recent Figures",
            "",
            "No figures added yet.",
            "",
            "Run `slidedeck add` to add your first figure.",
        ])
        return "\n".join(lines)

    # Sort all slides by date (newest first)
    sorted_slides = sorted(slides, key=lambda s: s["created"], reverse=True)
    recent_slides = sorted_slides[:count]

    # Get topic names for display
    topics = {t["id"]: t["name"] for t in registry["topics"]}

    for slide in recent_slides:
        lines.extend([
            "## " + slide["title"],
            "",
        ])
        _render_slide(slide, lines)

    return "\n".join(lines)


def build_styles_css() -> str:
    """Generate CSS for figure styling."""
    return """.reveal,
.reveal h1,
.reveal h2,
.reveal h3,
.reveal p,
.reveal li,
.reveal .slides {
    font-family: Arial, sans-serif !important;
}

/* Vertically center slide content when space allows */
.reveal .slides section {
    display: flex !important;
    flex-direction: column;
    justify-content: center;
}

/* Smaller headlines */
.reveal h1 {
    font-size: 1.4em;
    margin-bottom: 0.3em;
}

.reveal h2 {
    font-size: 1.1em;
    margin-bottom: 0.2em;
}

/* Center all images */
.reveal img {
    max-height: 65vh;
    width: auto;
    display: block;
    margin: 0 auto;
}

.reveal figure {
    margin: 0 auto;
}

/* Figure captions */
.reveal .caption {
    font-size: 0.3em;
    color: #333;
    text-align: left;
    margin-top: 0.5em;
    max-width: 95%;
    margin-left: auto;
    margin-right: auto;
    line-height: 1.3;
}

/* Scrollable table of contents */
.reveal .slide-menu-wrapper {
    overflow-y: auto;
}

#TOC {
    max-height: 80vh;
    overflow-y: auto;
}
"""


def build_slides(recent_count: int = 10) -> None:
    """Build all QMD files from the registry."""
    registry = load_registry()

    # Build slides.qmd
    slides_content = build_slides_qmd(registry)
    Path("slides.qmd").write_text(slides_content)
    click.echo("Generated slides.qmd")

    # Build recent.qmd
    recent_content = build_recent_qmd(registry, count=recent_count)
    Path("recent.qmd").write_text(recent_content)
    click.echo("Generated recent.qmd")

    # Build styles.css
    styles_content = build_styles_css()
    Path("styles.css").write_text(styles_content)
    click.echo("Generated styles.css")

    slide_count = len(registry.get("slides", []))
    click.echo("Build complete: " + str(slide_count) + " slides across " + str(len(registry["topics"])) + " topics")
