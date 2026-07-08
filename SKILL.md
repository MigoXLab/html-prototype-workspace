---
name: html-prototype-workspace
description: Use when building, packaging, or migrating static HTML prototype workspaces with one root index.html, module tab folders, per-tab assets, optional shared/design-system resources, iframe navigation, avatar subpages, hash deep links, module completeness checks, or legacy pages whose resources need ownership cleanup.
---

# HTML Prototype Workspace

## Overview

Build static multi-page HTML prototypes around one shell page and independent module folders. The invariant is:

```text
project/
├── index.html
└── tabs/
    └── <module-id>/
        ├── index.html
        └── assets/
```

Use an iframe-based content pane by default so each module page keeps its own HTML, styles, scripts, dimensions, and private assets isolated from other modules. This skill is for design/product handoff prototypes, not Vite/React/framework conversion.

`design-system/` and `shared/` are optional top-level folders. Add them only when the project needs reusable design tokens, common shell CSS/JS, shared icons, or cross-tab resources. Product-only prototypes may omit both.

Migration means making the target directory the new source of truth, not wrapping the old project. Do not finish with tab pages that merely load a legacy all-in-one HTML page or depend on an old unclassified asset tree.

## Directory Contract

Use this contract for any business domain. The root folder name and tab names should come from the project context, not from this skill.

```text
<project-name>/
├── index.html                 # entry shell: sidebar, avatar popover, tab content loading
├── design-system/             # optional: design rules and design variables
│   ├── atoms.html             # optional: basic atom/component examples
│   └── tokens/
├── shared/                    # optional: cross-tab public resources
│   ├── css/
│   ├── js/
│   └── assets/
└── tabs/                      # each business tab owns its page and private assets
    ├── <module-id>/
    │   ├── index.html         # module entry HTML
    │   └── assets/            # module images, icons, media, samples
    └── <subpage-id>/
        ├── index.html
        └── assets/
```

Rules:

- Every primary tab route must point to `tabs/<module-id>/index.html`.
- Every module owns its private static resources under `tabs/<module-id>/assets/`.
- `shared/` is only for resources reused by more than one tab or by the shell.
- `shared/assets/` is not a fallback dump. A resource may enter `shared/` only when references prove it is used by the shell, design-system, or two or more tabs.
- When ownership is unclear, keep the resource with the most likely owning tab and note the uncertainty, or ask the user. Do not put uncertain resources in `shared/` by default.
- Asset folders whose names match module IDs, nav labels, or content domains are tab-private by default, such as `paper`, `dataset`, `compute`, `tool`, `reference`, `samples`, or project-specific module names.
- Do not leave `tabs/<module-id>/assets/` empty when that tab references private images, icons, media, JSON, fonts, or samples.
- Every referenced static resource must have an owner: the shell, one tab, multiple tabs, or design-system.
- `design-system/` is only for design tokens, atoms, and design rules.
- Shell behavior belongs in root `index.html`, or in `shared/js/shell.js` when `shared/` exists.
- Subpages opened from an avatar popover, modal, or secondary navigation may live under `tabs/<subpage-id>/`, but should not become primary sidebar tabs unless the user asks.

## Discovery Example

When the user explicitly names Discovery or provides this convention, use these module IDs and labels. Otherwise, do not force these names onto other projects.

```text
discovery-ui/
├── index.html                 # entry shell: sidebar, avatar popover, tab content loading
├── design-system/             # optional for product prototype
│   ├── atoms.html
│   └── tokens/
├── shared/                    # optional for product prototype
│   ├── css/
│   ├── js/
│   └── assets/
└── tabs/
    ├── paper/                 # 论文发现
    │   ├── index.html
    │   └── assets/
    ├── space/                 # 课题空间
    │   ├── index.html
    │   └── assets/
    ├── app/                   # 科研应用
    │   ├── index.html
    │   └── assets/
    ├── tool/                  # 科学工具
    │   ├── index.html
    │   └── assets/
    ├── dataset/               # 科学数据
    │   ├── index.html
    │   └── assets/
    ├── compute/               # 科学计算
    │   ├── index.html
    │   └── assets/
    └── usercenter/            # avatar popover subpage
        ├── index.html
        └── assets/
```

Discovery primary sidebar order: `paper`, `space`, `app`, `tool`, `dataset`, `compute`. `usercenter` is a secondary avatar subpage by default.

## Tab Naming

Choose tab IDs from the user's business context:

- Prefer existing business names, URLs, nav labels, or user-provided folder names.
- Use lowercase kebab-case or short lowercase slugs: `paper`, `space`, `user-center`, `sales-dashboard`.
- Do not invent Discovery names for non-Discovery projects.
- If two old pages map to the same tab ID, stop and ask which one is canonical.
- If the user provides a directory convention, that convention wins.

## Workflow

1. Inspect the existing project or source HTML pages.
2. Identify the shell page, intended primary tabs, secondary subpages, and local assets.
   - for migrations, write a source-to-target module map before moving files
   - every source module must map to a target tab, secondary subpage, shared area, or explicit "excluded" note
3. Create or update root `index.html` with:
   - persistent sidebar or tab rail
   - optional avatar hover/popover route for secondary pages
   - iframe content pane
   - route data in one place
   - active tab state
   - hash deep links such as `#paper` or `#sales-dashboard`
   - loading and error state
4. Keep each tab independently openable at `tabs/<module-id>/index.html`.
5. Preserve or fix relative asset paths inside each module.
6. Verify every primary tab, secondary avatar route, hash link, and direct module page.

## Migrating Existing Projects

Use this when an existing prototype has scattered HTML files, old tab names, mixed assets, or no consistent shell.

The migration is incomplete if the result only preserves visual behavior by pointing tabs at shared legacy HTML, shared legacy JS, or an undivided `src/`/`assets/` folder. Compatibility wrappers are acceptable only as a temporary step while working, not as the final deliverable.

1. Inventory current pages:
   - list all `.html` files that represent screens or modules
   - list global CSS/JS/assets
   - list page-local images, icons, fonts, samples
   - list which tab or shell references each asset
   - build an asset usage matrix: original asset path, referencing HTML/CSS/JS, inferred owner, target path
2. Decide the target root and tab map:
   - root can be any project name, such as `discovery-ui`
   - map each old page/folder to `tabs/<module-id>/index.html`
   - only use a domain-specific mapping table when the user provided one
   - do not start moving files until every discovered module has a target or an explicit exclusion reason
3. Split each module into a real standalone tab page:
   - page HTML goes to `tabs/<module-id>/index.html`
   - if the source is one large HTML file with many internal views, extract each view into its own tab `index.html`
   - remove unrelated hidden views, unrelated module DOM, and old tab-switching code from each extracted tab
   - keep only the markup, styles, data, and scripts required for that tab plus intentional shared dependencies
4. Classify and move resources with tab ownership as the default:
   - resources referenced by exactly one tab go under that tab's `assets/`
   - resources referenced only by one tab's CSS or JS also go under that tab's `assets/`
   - resources referenced by the shell or two or more tabs may go under `shared/assets/`, `shared/css/`, or `shared/js/`
   - design tokens, atoms, and reusable design rules go under `design-system/`
   - page-specific CSS/JS should stay inline in that tab page or live in that tab's assets folder
   - module-named asset folders must move to their matching tab unless the usage matrix proves they are shared
   - if an asset cannot be classified from references, do not put it in `shared/`; place it under the most likely tab and document the assumption, or ask the user
   - do not keep an undivided `shared/legacy/`, `src/`, or root `assets/` dump as the final answer
5. Update paths:
   - fix image/font/script/CSS links after moving files
   - keep paths relative, never absolute filesystem paths
   - route shell entries to `tabs/<module-id>/index.html`
6. Preserve page isolation:
   - for product prototypes, keep page-specific CSS/JS inline in each module `index.html` when possible
   - for UI/design-system packages, use `shared/` for true cross-tab shell or component resources
   - opening one tab directly must not require another tab's DOM, state, or private assets
7. Clean up cautiously:
   - do not delete old files until routes and assets are verified
   - leave unrelated files untouched
   - once verified, remove empty placeholder `assets/` folders only if the tab truly has no private assets
8. Verify:
   - compare the source module inventory against the target tab map
   - every source module is present, intentionally merged, moved to a secondary subpage, or explicitly excluded
   - every primary target tab exists as `tabs/<module-id>/index.html`
   - every primary target tab is present in the shell route data
   - every shell route points to an existing tab `index.html`
   - root `index.html` loads
   - every tab opens
   - direct module pages open
   - assets render
   - hash links and active states work
   - avatar/subpage routes work if present
   - no tab route points to a legacy all-in-one page
   - no module-private asset remains in `shared/` or an old root asset dump
   - no module-named or content-specific asset folder remains under `shared/assets/` unless the final report explains the shared references
   - every non-empty `shared/assets/` subfolder has evidence of shell use, design-system use, or two-or-more-tab use

Migration completion report:

- Include a source-to-target module map in the final response.
- For each source module, state the target path, status, and notes: `migrated`, `merged into <module>`, `secondary subpage`, or `excluded by request`.
- Include an asset ownership summary: `tabs/<module>/assets/` contents, `shared/assets/` contents, and why each shared asset group is shared.
- Include a route check: every primary tab in the map appears in the shell route data, and every route target exists on disk.
- Do not call the migration complete when a discovered source module has no target, no merge note, and no exclusion reason.
- Do not call the migration complete when `shared/assets/` contains likely tab-private folders without shared-reference evidence.

Discovery migration examples, only when applicable:

| old name | canonical Discovery target |
| --- | --- |
| `papers`, `paper-discovery` | `tabs/paper/` |
| `topics`, `space`, `project-space` | `tabs/space/` |
| `research-tools`, `tools` | `tabs/tool/` |
| `research-compute`, `compute` | `tabs/compute/` |
| `datasets`, `data` | `tabs/dataset/` |
| `apps`, `applications` | `tabs/app/` |

## Generator

For a straightforward static prototype with pages that are already separated, use `scripts/build_sidebar_shell.py` when Python is available:

```bash
python /path/to/html-prototype-workspace/scripts/build_sidebar_shell.py \
  --title "HTML Prototype" \
  --output ./project/index.html \
  --page "模块一=./project/tabs/module-one/index.html" \
  --page "模块二=./project/tabs/module-two/index.html"
```

Use repeated `--page "Label=path/to/page.html"` arguments in sidebar order. If the label is omitted, the script derives it from the filename.

Use `--copy-pages` when source pages live outside the target project and should be packaged for handoff. With `--copy-pages`, the script copies the source page's containing folder into `tabs/<tab-id>/` so the page HTML and local assets stay together. Prefer source pages named `index.html` for clean routes.

Do not use the generator as a substitute for a full legacy migration. If the source is one large HTML page with multiple internal views, first split real tab pages and classify assets, then use or adapt the shell.

The generator renders every `--page` as a sidebar item. Add avatar subpages manually unless the user explicitly wants them in the primary sidebar.

## No-Python Fallback

Python is optional. If `python` or `python3` is unavailable, copy `assets/sidebar-shell-template/index.html` into the project as the root shell and edit:

- document `<title>` and `.brand-title`
- `routes` array
- each route's `id`, `label`, and `src`

Keep route `src` values relative to the shell, for example `tabs/module-one/index.html`. Put static resources beside module HTML under `assets/`. Verify in a browser after editing.

## Implementation Notes

- Build the actual navigable prototype as the first screen, not a marketing/landing page.
- Keep navigation compact, scannable, and stable.
- Use route data in one place, then render navigation from that data.
- Make the first primary tab the default unless the user specifies otherwise.
- Store active route in `location.hash` so reviewers can share links.
- Do not use `fetch()` to load local page HTML from `file://`; use an iframe or run a local server.
- Do not move module-private assets into `shared/`.
- Do not add a build tool or framework unless explicitly requested.
- Keep generated paths relative.

## Validation

When practical, run a local static server from the project directory:

```bash
python3 -m http.server 8000
```

Then verify desktop and mobile widths. If using browser automation, check that the iframe `src` changes for each tab, the active route matches the hash, direct tab pages open, and no page appears blank.
