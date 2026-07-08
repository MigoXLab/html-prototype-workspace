#!/usr/bin/env python3
"""Generate an iframe-based sidebar shell for separate HTML pages."""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
from pathlib import Path
from urllib.parse import quote


def slugify(value: str, fallback: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or fallback


def page_label_from_path(path: Path) -> str:
    label = path.stem.replace("_", " ").replace("-", " ").strip()
    return " ".join(part.capitalize() for part in label.split()) or path.name


def page_id_from_label_path(label: str, raw_path: str, index: int) -> str:
    path = Path(raw_path)
    fallback = f"page-{index}"
    path_stem = path.stem
    if path_stem.lower() in {"index", "page"} and path.parent.name:
        path_stem = path.parent.name
    fallback = slugify(path_stem, fallback)
    return slugify(label, fallback)


def parse_page_specs(specs: list[str]) -> list[dict[str, str]]:
    pages: list[dict[str, str]] = []
    seen_ids: set[str] = set()

    for index, spec in enumerate(specs, start=1):
        if "=" in spec:
            label, raw_path = spec.split("=", 1)
            label = label.strip()
            raw_path = raw_path.strip()
        else:
            raw_path = spec.strip()
            label = page_label_from_path(Path(raw_path))

        if not raw_path:
            raise SystemExit(f"Empty path in --page value: {spec!r}")

        page_id = page_id_from_label_path(label, raw_path, index)
        base_id = page_id
        suffix = 2
        while page_id in seen_ids:
            page_id = f"{base_id}-{suffix}"
            suffix += 1
        seen_ids.add(page_id)

        pages.append(
            {
                "id": page_id,
                "label": label or page_label_from_path(Path(raw_path)),
                "source": raw_path,
            }
        )

    return pages


def output_file_from_arg(output: str) -> Path:
    output_path = Path(output)
    if output_path.suffix.lower() == ".html":
        return output_path
    return output_path / "index.html"


def to_url_path(path: str) -> str:
    return quote(path.replace("\\", "/"), safe="/.#?=&:%-")


def copy_tab_folder(source: Path, target_dir: Path) -> Path:
    source_parent = source.parent.resolve()
    target_dir = target_dir.resolve()

    if source_parent == target_dir:
        return target_dir / source.name

    shutil.copytree(
        source_parent,
        target_dir,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns(
            ".DS_Store",
            "__MACOSX",
            ".git",
            ".svn",
            "node_modules",
            "dist",
            ".next",
            ".vite",
        ),
    )
    return target_dir / source.name


def prepare_sources(
    pages: list[dict[str, str]], output_file: Path, copy_pages: bool
) -> list[dict[str, str]]:
    output_dir = output_file.parent.resolve()
    prepared: list[dict[str, str]] = []

    pages_dir = output_dir / "tabs"
    if copy_pages:
        pages_dir.mkdir(parents=True, exist_ok=True)

    for page in pages:
        source = Path(page["source"]).expanduser()
        source = source if source.is_absolute() else Path.cwd() / source
        source = source.resolve()

        if not source.exists():
            raise SystemExit(f"Page does not exist: {source}")
        if source.suffix.lower() not in {".html", ".htm"}:
            raise SystemExit(f"Page must be an HTML file: {source}")

        if copy_pages:
            target = copy_tab_folder(source, pages_dir / page["id"])
            iframe_src = target.relative_to(output_dir).as_posix()
        else:
            iframe_src = Path(os.path.relpath(source, output_dir)).as_posix()

        prepared.append(
            {
                "id": page["id"],
                "label": page["label"],
                "src": to_url_path(iframe_src),
            }
        )

    return prepared


def render_shell(title: str, pages: list[dict[str, str]]) -> str:
    title_html = html.escape(title)
    pages_json = json.dumps(pages, ensure_ascii=False, indent=2)
    title_json = json.dumps(title, ensure_ascii=False)
    first_id = pages[0]["id"]

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title_html}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f6f7f9;
      --panel: #ffffff;
      --text: #17181c;
      --muted: #687083;
      --line: #dfe3ea;
      --active: #2563eb;
      --active-bg: #e8f0ff;
      --shadow: 0 12px 30px rgba(18, 28, 45, 0.08);
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      min-height: 100vh;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--text);
      background: var(--bg);
    }}

    .app-shell {{
      display: grid;
      grid-template-columns: 248px minmax(0, 1fr);
      min-height: 100vh;
    }}

    .sidebar {{
      display: flex;
      flex-direction: column;
      gap: 18px;
      padding: 22px 16px;
      border-right: 1px solid var(--line);
      background: var(--panel);
    }}

    .brand {{
      min-height: 40px;
      padding: 0 8px;
    }}

    .brand-title {{
      margin: 0;
      font-size: 15px;
      font-weight: 700;
      line-height: 1.25;
    }}

    .brand-subtitle {{
      margin: 4px 0 0;
      color: var(--muted);
      font-size: 12px;
    }}

    .nav {{
      display: grid;
      gap: 4px;
    }}

    .nav-button {{
      width: 100%;
      min-height: 38px;
      padding: 9px 10px;
      border: 0;
      border-radius: 8px;
      color: var(--muted);
      background: transparent;
      font: inherit;
      font-size: 14px;
      line-height: 1.25;
      text-align: left;
      cursor: pointer;
    }}

    .nav-button:hover {{
      color: var(--text);
      background: #f1f3f7;
    }}

    .nav-button:focus-visible {{
      outline: 2px solid var(--active);
      outline-offset: 2px;
    }}

    .nav-button[aria-current="page"] {{
      color: var(--active);
      background: var(--active-bg);
      font-weight: 700;
    }}

    .content {{
      display: grid;
      grid-template-rows: auto minmax(0, 1fr);
      min-width: 0;
      min-height: 100vh;
    }}

    .content-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      min-height: 68px;
      padding: 16px 22px;
      border-bottom: 1px solid var(--line);
      background: rgba(255, 255, 255, 0.86);
      backdrop-filter: blur(14px);
    }}

    .page-title {{
      margin: 0;
      overflow: hidden;
      font-size: 18px;
      font-weight: 750;
      line-height: 1.2;
      text-overflow: ellipsis;
      white-space: nowrap;
    }}

    .open-link {{
      flex: 0 0 auto;
      color: var(--active);
      font-size: 13px;
      font-weight: 650;
      text-decoration: none;
    }}

    .open-link:hover {{
      text-decoration: underline;
    }}

    .frame-wrap {{
      position: relative;
      min-height: 0;
      padding: 16px;
    }}

    .status {{
      position: absolute;
      inset: 16px;
      display: none;
      place-items: center;
      border: 1px dashed var(--line);
      border-radius: 8px;
      color: var(--muted);
      background: rgba(255, 255, 255, 0.75);
      z-index: 1;
    }}

    .status.is-visible {{
      display: grid;
    }}

    iframe {{
      display: block;
      width: 100%;
      height: 100%;
      min-height: calc(100vh - 100px);
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #ffffff;
      box-shadow: var(--shadow);
    }}

    @media (max-width: 760px) {{
      .app-shell {{
        grid-template-columns: 1fr;
        grid-template-rows: auto minmax(0, 1fr);
      }}

      .sidebar {{
        gap: 12px;
        padding: 14px 12px 10px;
        border-right: 0;
        border-bottom: 1px solid var(--line);
      }}

      .brand {{
        padding: 0 2px;
      }}

      .nav {{
        display: flex;
        gap: 6px;
        overflow-x: auto;
        padding-bottom: 2px;
      }}

      .nav-button {{
        flex: 0 0 auto;
        width: auto;
        white-space: nowrap;
      }}

      .content {{
        min-height: 0;
      }}

      .content-header {{
        min-height: 56px;
        padding: 12px;
      }}

      .frame-wrap {{
        padding: 10px;
      }}

      .status {{
        inset: 10px;
      }}

      iframe {{
        min-height: calc(100vh - 170px);
      }}
    }}
  </style>
</head>
<body>
  <div class="app-shell">
    <aside class="sidebar" aria-label="Prototype navigation">
      <div class="brand">
        <h1 class="brand-title">{title_html}</h1>
        <p class="brand-subtitle">HTML prototype</p>
      </div>
      <nav class="nav" id="tabNav" aria-label="Pages"></nav>
    </aside>

    <main class="content">
      <header class="content-header">
        <h2 class="page-title" id="pageTitle"></h2>
        <a class="open-link" id="openLink" href="#" target="_blank" rel="noreferrer">Open page</a>
      </header>
      <section class="frame-wrap" aria-live="polite">
        <div class="status is-visible" id="status">Loading page...</div>
        <iframe id="contentFrame" title="Prototype page"></iframe>
      </section>
    </main>
  </div>

  <script>
    const routes = {pages_json};
    const defaultRouteId = "{first_id}";
    const nav = document.getElementById("tabNav");
    const frame = document.getElementById("contentFrame");
    const status = document.getElementById("status");
    const pageTitle = document.getElementById("pageTitle");
    const openLink = document.getElementById("openLink");
    const shellTitle = {title_json};

    function routeFromHash() {{
      const id = decodeURIComponent(window.location.hash.replace(/^#/, ""));
      return routes.find((route) => route.id === id) || routes.find((route) => route.id === defaultRouteId) || routes[0];
    }}

    function setActive(route) {{
      document.querySelectorAll(".nav-button").forEach((button) => {{
        const isActive = button.dataset.routeId === route.id;
        button.setAttribute("aria-current", isActive ? "page" : "false");
      }});
    }}

    function showRoute(route) {{
      if (!route) return;
      setActive(route);
      pageTitle.textContent = route.label;
      openLink.href = route.src;
      status.textContent = "Loading page...";
      status.classList.add("is-visible");
      if (frame.getAttribute("src") !== route.src) {{
        frame.src = route.src;
      }} else {{
        status.classList.remove("is-visible");
      }}
      document.title = `${{route.label}} - ${{shellTitle}}`;
    }}

    routes.forEach((route) => {{
      const button = document.createElement("button");
      button.type = "button";
      button.className = "nav-button";
      button.dataset.routeId = route.id;
      button.textContent = route.label;
      button.addEventListener("click", () => {{
        window.location.hash = encodeURIComponent(route.id);
      }});
      nav.appendChild(button);
    }});

    frame.addEventListener("load", () => {{
      status.classList.remove("is-visible");
    }});

    window.addEventListener("hashchange", () => showRoute(routeFromHash()));

    if (!window.location.hash) {{
      window.location.replace(`#${{encodeURIComponent(defaultRouteId)}}`);
    }} else {{
      showRoute(routeFromHash());
    }}
  </script>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate one sidebar/tab shell HTML file for separate source HTML pages."
    )
    parser.add_argument("--title", default="HTML Prototype", help="Shell title.")
    parser.add_argument(
        "--output",
        default="./index.html",
        help="Output HTML file or output directory. Directories receive index.html.",
    )
    parser.add_argument(
        "--page",
        action="append",
        required=True,
        help='Page spec in sidebar order. Use "Label=path/to/page.html" or just a path.',
    )
    parser.add_argument(
        "--copy-pages",
        action="store_true",
        help="Copy each source page folder into output/tabs/<tab-id> so HTML and local assets stay together.",
    )

    args = parser.parse_args()
    pages = parse_page_specs(args.page)
    output_file = output_file_from_arg(args.output).expanduser()
    output_file = output_file if output_file.is_absolute() else Path.cwd() / output_file
    output_file.parent.mkdir(parents=True, exist_ok=True)

    prepared = prepare_sources(pages, output_file, args.copy_pages)
    output_file.write_text(render_shell(args.title, prepared), encoding="utf-8")
    print(f"Wrote {output_file}")


if __name__ == "__main__":
    main()
