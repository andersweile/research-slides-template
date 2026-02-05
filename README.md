# Research Slides Template

A cookiecutter template for creating rolling research slide decks with Quarto Reveal.js. Track your research figures over time, organized by topic, with academic-style captions.

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

# Build the slides
slidedeck build

# Preview in browser
quarto preview slides.qmd
```

## Project Structure

```
research_slides/
├── _quarto.yml          # Quarto project configuration
├── slides.yaml          # Figure registry (metadata for all slides)
├── slides.qmd           # Auto-generated main slide deck
├── recent.qmd           # Auto-generated recent figures view
├── index.qmd            # Landing page with navigation
├── styles.css           # Auto-generated styling
├── figures/             # Figure images organized by topic
│   ├── data_exploration/
│   ├── modeling/
│   └── results/
├── pyproject.toml       # Python package definition
└── src/slidedeck/       # CLI tool source
```

## CLI Commands

### Add a figure

```bash
slidedeck add <figure_path> [options]
```

**Options:**
| Option | Short | Description |
|--------|-------|-------------|
| `--title` | `-T` | Slide title (shown at top). Inferred from filename if omitted. |
| `--caption` | `-c` | Figure caption (shown below figure, like in papers) |
| `--notes` | `-n` | Speaker notes (only visible in presenter view) |
| `--topic` | `-t` | Topic ID. Inferred from path if figure is in `figures/<topic>/` |
| `--tags` | | Comma-separated tags for organization |
| `--copy` | | Copy the figure file into the `figures/` directory |

**Examples:**

```bash
# Minimal - infers topic from path, title from filename
slidedeck add figures/data_exploration/correlation_matrix.png

# With caption (appears below figure)
slidedeck add figures/modeling/coefficients.png \
  --title "Regression Coefficients" \
  --caption "Standardized coefficients with 95% CI from Model 2"

# With speaker notes
slidedeck add figures/results/main_finding.png \
  --title "Key Result" \
  --caption "Treatment effect sizes across conditions" \
  --notes "Emphasize the significance of Treatment A"

# Copy external figure into project
slidedeck add ~/Downloads/plot.png --topic results --title "New Finding" --copy
```

### Build slides

Regenerates `slides.qmd` and `recent.qmd` from the registry:

```bash
slidedeck build
```

**Options:**
| Option | Short | Description |
|--------|-------|-------------|
| `--recent-count` | `-n` | Number of figures in recent view (default: 10) |

### Preview

Build and open in browser:

```bash
slidedeck preview
```

### Git history tools

View the git history of a figure:

```bash
slidedeck history figures/data_exploration/my_plot.png
```

Generate an HTML comparison of all versions:

```bash
slidedeck compare figures/data_exploration/my_plot.png --output comparison.html
```

## Rendering Options

### Slide presentation (default)

```bash
quarto preview slides.qmd      # Live preview
quarto render slides.qmd       # Build HTML
```

### PDF export

```bash
quarto render slides.qmd --to pdf
```

### Recent figures view

Shows the N most recent figures across all topics:

```bash
quarto preview recent.qmd
```

## Slide Format

Each slide shows:
1. **Title** at the top
2. **Figure** centered
3. **Caption** below the figure (small italic text)
4. **Speaker notes** visible only in presenter view (press `S`)

Example generated slide:

```markdown
## Regression Coefficients

![Standardized coefficients with 95% CI from Model 2](figures/modeling/coefficients.png)

::: {.notes}
Model selected based on AIC comparison
:::
```

## Topics

Default topics (defined in `slides.yaml`):
- `data_exploration` - EDA, distributions, correlations
- `modeling` - Model development, diagnostics
- `results` - Final results, key findings

Add custom topics by editing `slides.yaml`:

```yaml
topics:
  - id: data_exploration
    name: "Data Exploration"
    order: 1
  - id: methods
    name: "Methods"
    order: 2
  - id: results
    name: "Results"
    order: 3
```

## Workflow Integration

### From notebooks/scripts

```python
import matplotlib.pyplot as plt

# Create and save figure
fig, ax = plt.subplots()
ax.plot(x, y)
plt.savefig("research_slides/figures/results/my_plot.png", dpi=150)

# Then in terminal:
# cd research_slides && slidedeck add figures/results/my_plot.png --caption "..."
```

### Typical workflow

1. Generate figure in analysis notebook
2. Save to appropriate `figures/<topic>/` directory
3. Run `slidedeck add` with title and caption
4. Run `slidedeck build` to regenerate slides
5. Preview with `quarto preview slides.qmd`

## Requirements

- Python 3.10+
- [Quarto](https://quarto.org/docs/get-started/)
- [Cookiecutter](https://cookiecutter.readthedocs.io/)
