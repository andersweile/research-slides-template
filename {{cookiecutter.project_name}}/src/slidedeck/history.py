"""Git history inspection for figures."""

import base64
import subprocess
from pathlib import Path

import click


def get_figure_history(figure_path: str) -> list[dict]:
    """Get git commits that modified this figure.

    Returns a list of dicts with keys: commit, date, message
    """
    try:
        result = subprocess.run(
            ["git", "log", "--format=%H|%ai|%s", "--follow", "--", figure_path],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError:
        return []

    history = []
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        parts = line.split("|", 2)
        if len(parts) == 3:
            history.append({
                "commit": parts[0],
                "date": parts[1],
                "message": parts[2],
            })
    return history


def extract_figure_version(figure_path: str, commit: str, output_path: Path) -> bool:
    """Extract a specific version of a figure from git history.

    Returns True if successful, False otherwise.
    """
    try:
        result = subprocess.run(
            ["git", "show", commit + ":" + figure_path],
            capture_output=True,
            check=True,
        )
        output_path.write_bytes(result.stdout)
        return True
    except subprocess.CalledProcessError:
        return False


def show_history(figure_path: str) -> None:
    """Display git history for a figure."""
    history = get_figure_history(figure_path)

    if not history:
        click.echo("No git history found for " + figure_path)
        click.echo("(File may not be tracked by git or has no commits)")
        return

    click.echo("Git history for " + figure_path + ":")
    click.echo("-" * 60)

    for i, entry in enumerate(history):
        click.echo("\n[" + str(i + 1) + "] " + entry["date"])
        click.echo("    Commit: " + entry["commit"][:8])
        click.echo("    Message: " + entry["message"])

    click.echo("\n" + str(len(history)) + " version(s) found")
    click.echo("\nUse 'slidedeck compare' to generate a visual comparison.")


def generate_comparison(figure_path: str, output: str) -> None:
    """Generate an HTML page showing all versions of a figure side by side."""
    history = get_figure_history(figure_path)

    if not history:
        click.echo("No git history found for " + figure_path)
        return

    if len(history) < 2:
        click.echo("Only one version found. Nothing to compare.")
        return

    # Create temporary directory for extracted versions
    temp_dir = Path(".figure_history_temp")
    temp_dir.mkdir(exist_ok=True)

    # Extract each version
    versions = []
    for i, entry in enumerate(history):
        version_path = temp_dir / ("v" + str(i + 1) + "_" + entry["commit"][:8] + ".png")
        if extract_figure_version(figure_path, entry["commit"], version_path):
            # Read and base64 encode for embedding in HTML
            with open(version_path, "rb") as f:
                img_data = base64.b64encode(f.read()).decode()
            versions.append({
                "index": i + 1,
                "commit": entry["commit"][:8],
                "date": entry["date"],
                "message": entry["message"],
                "data": img_data,
            })

    # Generate HTML
    html = generate_comparison_html(figure_path, versions)
    Path(output).write_text(html)

    # Cleanup temp directory
    for f in temp_dir.iterdir():
        f.unlink()
    temp_dir.rmdir()

    click.echo("Generated comparison: " + output)
    click.echo("Showing " + str(len(versions)) + " versions")


def generate_comparison_html(figure_path: str, versions: list[dict]) -> str:
    """Generate HTML content for the comparison page."""
    version_cards = []
    for v in versions:
        card = """
        <div class="version-card">
            <h3>Version """ + str(v["index"]) + """</h3>
            <p class="meta">
                <span class="commit">""" + v["commit"] + """</span>
                <span class="date">""" + v["date"] + """</span>
            </p>
            <p class="message">""" + v["message"] + """</p>
            <img src="data:image/png;base64,""" + v["data"] + """" alt="Version """ + str(v["index"]) + """">
        </div>
        """
        version_cards.append(card)

    # Build HTML using string concatenation to avoid Jinja2 conflicts with braces
    html_parts = [
        """<!DOCTYPE html>
<html>
<head>
    <title>Figure History: """,
        figure_path,
        """</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        h1 {
            color: #333;
            border-bottom: 2px solid #007acc;
            padding-bottom: 10px;
        }
        .versions {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
        }
        .version-card {
            background: white;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .version-card h3 {
            margin-top: 0;
            color: #007acc;
        }
        .meta {
            font-size: 0.9em;
            color: #666;
        }
        .commit {
            font-family: monospace;
            background: #f0f0f0;
            padding: 2px 6px;
            border-radius: 3px;
        }
        .date {
            margin-left: 10px;
        }
        .message {
            font-style: italic;
            color: #555;
        }
        .version-card img {
            max-width: 100%;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <h1>Figure History: """,
        figure_path,
        """</h1>
    <p>""",
        str(len(versions)),
        """ versions found (newest first)</p>
    <div class="versions">
        """,
        "".join(version_cards),
        """
    </div>
</body>
</html>
""",
    ]
    return "".join(html_parts)
