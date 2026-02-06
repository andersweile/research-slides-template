# Research Slides Template

A cookiecutter template for creating rolling research slide decks with Quarto RevealJS. Track your research figures over time, organized by topic, with academic-style captions.

## Quick Start

```bash
# Create a new slide deck project
cookiecutter ~/Library/CloudStorage/OneDrive-ITU/Tools/Templates/research_slides_template/

# Enter the project
cd research_slides

# Install the CLI tool
pip install -e .

# Add your first figure
slidedeck add figures/data_exploration/my_plot.png \
  --title "My Analysis" \
  --caption "Distribution of values (N=100)"

# Build and preview
slidedeck build
quarto preview
```

## How It Works

`slides.yaml` is the single source of truth. All slide content, topics, and the deck title are defined there. The `.qmd` files are generated — never edit them by hand.

**Workflow: edit `slides.yaml` -> run `slidedeck build` -> preview with `quarto preview`.**

### Project Structure

```
research_slides/
├── slides.yaml          # Single source of truth (all slide metadata + content)
├── slides.qmd           # Generated — main slide deck
├── recent.qmd           # Generated — recent figures view
├── styles.css           # Generated — slide styling
├── _quarto.yml          # Quarto project config (navbar, theme)
├── index.qmd            # Landing page with navigation
├── figures/             # Figure images organized by topic
│   ├── data_exploration/
│   ├── modeling/
│   └── results/
├── pyproject.toml       # Python package definition
└── src/slidedeck/       # CLI tool source
```

## Slide Types

### Figure slides

Have a `figure` field pointing to an image. Optionally include a `caption`.

```yaml
- id: 2026-02-05_my_plot
  topic: results
  title: My Plot
  figure: figures/results/my_plot.png
  caption: "Description of the figure."
  created: '2026-02-05'
  tags: []
```

### Text-only slides

Have a `content` field with raw markdown instead of a figure. These are automatically scrollable when content overflows.

```yaml
- id: next_steps
  topic: results
  title: Next Steps
  content: |
    **Analysis**

    - Task one
    - Task two

    **Writing**

    - Draft introduction
  created: '2026-02-05'
  tags: []
```

### Mixed slides

Can have both `figure` and `content` — the figure renders first, then the markdown below it.

## Slide Schema

Each slide in `slides.yaml` supports these fields:

| Field     | Required | Description                                    |
|-----------|----------|------------------------------------------------|
| `id`      | yes      | Unique identifier (used as HTML anchor)        |
| `topic`   | yes      | Topic ID (must match a topic in `topics:`)     |
| `title`   | yes      | Slide heading                                  |
| `figure`  | no       | Path to figure image                           |
| `caption` | no       | Caption text below the figure                  |
| `content` | no       | Raw markdown content (for text-only slides)    |
| `notes`   | no       | Speaker notes (only visible in presenter view) |
| `created` | yes      | Date string (YYYY-MM-DD)                       |
| `tags`    | no       | List of tags                                   |

## CLI Commands

### `slidedeck add`

Add a figure slide to the registry:

```bash
# Minimal — infers topic from path, title from filename
slidedeck add figures/data_exploration/correlation_matrix.png

# With caption
slidedeck add figures/modeling/coefficients.png \
  --title "Regression Coefficients" \
  --caption "Standardized coefficients with 95% CI"

# Copy external figure into project
slidedeck add ~/Downloads/plot.png --topic results --title "New Finding" --copy
```

| Option | Short | Description |
|--------|-------|-------------|
| `--title` | `-T` | Slide title. Inferred from filename if omitted. |
| `--caption` | `-c` | Figure caption (below figure) |
| `--notes` | `-n` | Speaker notes (presenter view only) |
| `--topic` | `-t` | Topic ID. Inferred from path if in `figures/<topic>/` |
| `--tags` | | Comma-separated tags |
| `--copy` | | Copy figure file into `figures/` directory |

### `slidedeck build`

Regenerates `slides.qmd`, `recent.qmd`, and `styles.css` from `slides.yaml`:

```bash
slidedeck build
```

### `slidedeck preview`

Build and open in browser:

```bash
slidedeck preview
```

### `slidedeck history` / `slidedeck compare`

View git history of a figure, or generate an HTML comparison of all versions:

```bash
slidedeck history figures/results/my_plot.png
slidedeck compare figures/results/my_plot.png -o comparison.html
```

## Editing Slides

- **Titles, captions, content:** Edit the slide entry in `slides.yaml`, then `slidedeck build`.
- **Replacing a figure:** Overwrite the image file in `figures/` with the same filename. No YAML change needed.
- **Deck title:** Change the top-level `title:` field in `slides.yaml`.
- **Topics:** Edit the `topics:` list in `slides.yaml`. Each topic has `id`, `name`, and `order`.

## Workflow Integration

```python
import matplotlib.pyplot as plt

# Save figure to the project
fig, ax = plt.subplots()
ax.plot(x, y)
plt.savefig("research_slides/figures/results/my_plot.png", dpi=150)

# Then in terminal:
# cd research_slides && slidedeck add figures/results/my_plot.png --caption "..."
# slidedeck build
```

## Requirements

- Python 3.10+
- [Quarto](https://quarto.org/docs/get-started/)
- [Cookiecutter](https://cookiecutter.readthedocs.io/)
