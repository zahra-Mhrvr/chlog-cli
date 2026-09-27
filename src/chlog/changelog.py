"""
Takes the parsed commits and turns them into a Keep-a-Changelog-style
markdown document, grouped by section (Features, Bug Fixes, etc).
"""

from collections import defaultdict
from datetime import date

from chlog.parser import Commit

# the order sections show up in the output, doesn't matter for grouping
# but reads a lot better with Features/Fixes near the top
SECTION_ORDER = [
    "Features",
    "Bug Fixes",
    "Performance",
    "Refactoring",
    "Documentation",
    "Tests",
    "Build System",
    "CI",
    "Style",
    "Chores",
    "Reverts",
    "Other",
]


def group_by_section(commits: list[Commit]) -> dict[str, list[Commit]]:
    groups = defaultdict(list)
    for commit in commits:
        groups[commit.section].append(commit)
    return groups


def _format_commit_line(commit: Commit) -> str:
    scope_prefix = f"**{commit.scope}:** " if commit.scope else ""
    breaking_marker = " ⚠️ BREAKING" if commit.breaking else ""
    # strip the "type(scope): " prefix off the subject since the section
    # heading already tells you the type
    message = commit.subject.split(":", 1)[-1].strip()
    return f"- {scope_prefix}{message} (`{commit.hash}`){breaking_marker}"


def build_changelog(commits: list[Commit], version: str | None = None) -> str:
    if not commits:
        return "No changes found.\n"

    groups = group_by_section(commits)
    header_version = version or "Unreleased"
    lines = [f"## {header_version} - {date.today().isoformat()}", ""]

    for section in SECTION_ORDER:
        if section not in groups:
            continue
        lines.append(f"### {section}")
        for commit in groups[section]:
            lines.append(_format_commit_line(commit))
        lines.append("")

    return "\n".join(lines).strip() + "\n"
