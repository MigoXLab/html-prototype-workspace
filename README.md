# HTML Prototype Workspace

A Codex/Claude Code skill for organizing static HTML prototypes into a clean workspace with root entry, independent tab pages, per-tab assets, shared resources, and migration checks.

## What It Is For

Use this skill when creating, extending, packaging, or migrating static HTML prototype projects for product/design handoff.

The core project shape is:

```text
project/
├── index.html
└── tabs/
    └── <module-id>/
        ├── index.html
        └── assets/
```

Optional shared folders are supported when needed:

```text
project/
├── design-system/
└── shared/
```

## Install

Codex:

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo MigoXLab/html-prototype-workspace \
  --path . \
  --name html-prototype-workspace \
  --method git
```

Claude Code:

```bash
git clone https://github.com/MigoXLab/html-prototype-workspace.git ~/.claude/skills/html-prototype-workspace
```

Keep `SKILL.md` at the skill root.

## Use

```text
Please use $html-prototype-workspace to migrate this existing HTML prototype.

Project path:
Task type: initialize / continue development / migrate existing project
Modules:
Notes:
```

## License

MIT
