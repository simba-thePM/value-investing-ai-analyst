"""Loads skill definitions (markdown + YAML frontmatter) from skills/."""

import os
import re
import glob
import yaml

SKILLS_DIR = os.path.join(os.path.dirname(__file__), "..", "skills")

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


def load_skills() -> dict:
    """Returns {skill_id: {name, description, needs_rag, needs_tools, prompt_template}}."""
    skills = {}
    for path in sorted(glob.glob(os.path.join(SKILLS_DIR, "*.md"))):
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
        match = _FRONTMATTER_RE.match(raw)
        if not match:
            continue
        meta = yaml.safe_load(match.group(1))
        template = match.group(2).strip()
        skills[meta["id"]] = {
            "id": meta["id"],
            "name": meta["name"],
            "description": meta["description"],
            "needs_rag": meta.get("needs_rag", False),
            "needs_tools": meta.get("needs_tools", []),
            "prompt_template": template,
        }
    return skills
