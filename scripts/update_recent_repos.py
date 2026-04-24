#!/usr/bin/env python3
"""Update recent public repositories section in ReadMe.md."""

from __future__ import annotations

import json
import os
import re
import urllib.request
import urllib.error
from datetime import datetime, timezone

README_PATH = "ReadMe.md"
USERNAME = os.environ.get("GITHUB_USERNAME", "kanishksingh01")
MAX_REPOS = int(os.environ.get("MAX_REPOS", "6"))
START_MARKER = "<!--START_SECTION:recent_repos-->"
END_MARKER = "<!--END_SECTION:recent_repos-->"


def fetch_recent_repos(username: str, max_repos: int) -> list[dict]:
    url = f"https://api.github.com/users/{username}/repos?per_page=100&sort=updated"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": f"{username}-readme-updater",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            repos = json.load(response)
    except (urllib.error.URLError, TimeoutError) as exc:
        print(f"Warning: failed to fetch repositories: {exc}")
        return []

    filtered = [
        repo
        for repo in repos
        if not repo.get("private") and not repo.get("fork") and repo.get("name", "").lower() != username.lower()
    ]
    return filtered[:max_repos]


def fmt_date(iso_timestamp: str) -> str:
    dt = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00")).astimezone(timezone.utc)
    return dt.strftime("%Y-%m-%d")


def build_section(repos: list[dict]) -> str:
    if not repos:
        return "- No recent public repository activity found."

    lines = []
    for repo in repos:
        name = repo["name"]
        html_url = repo["html_url"]
        description = (repo.get("description") or "No description provided.").strip().replace("\n", " ")
        updated = fmt_date(repo["updated_at"])
        lines.append(f"- **[{name}]({html_url})** — {description} _(updated: {updated} UTC)_")
    return "\n".join(lines)


def update_readme(path: str, section_content: str) -> None:
    with open(path, "r", encoding="utf-8") as f:
        readme = f.read()

    pattern = rf"{re.escape(START_MARKER)}[\s\S]*?{re.escape(END_MARKER)}"
    replacement = f"{START_MARKER}\n{section_content}\n{END_MARKER}"

    if not re.search(pattern, readme):
        raise RuntimeError("Could not find recent repos section markers in ReadMe.md")

    updated = re.sub(pattern, replacement, readme)

    with open(path, "w", encoding="utf-8") as f:
        f.write(updated)


if __name__ == "__main__":
    recent = fetch_recent_repos(USERNAME, MAX_REPOS)
    content = build_section(recent)
    update_readme(README_PATH, content)
