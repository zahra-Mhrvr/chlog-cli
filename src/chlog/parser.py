"""
Reads git history and parses conventional-commit style subject lines
("feat: add thing", "fix(parser): handle empty input") into structured
data the changelog builder can group by type.
"""

import re
import subprocess
from dataclasses import dataclass

COMMIT_TYPES = {
    "feat": "Features",
    "fix": "Bug Fixes",
    "perf": "Performance",
    "refactor": "Refactoring",
    "docs": "Documentation",
    "test": "Tests",
    "build": "Build System",
    "ci": "CI",
    "chore": "Chores",
    "style": "Style",
    "revert": "Reverts",
}

# type(scope)!: subject   — scope and ! are both optional
SUBJECT_PATTERN = re.compile(r"^(?P<type>\w+)(\((?P<scope>[^)]+)\))?(?P<breaking>!)?:\s*(?P<subject>.+)$")


@dataclass
class Commit:
    hash: str
    subject: str
    type: str | None
    scope: str | None
    breaking: bool
    section: str  # human-readable group name, "Other" if it didn't parse


def _parse_subject(subject: str) -> tuple[str | None, str | None, bool]:
    match = SUBJECT_PATTERN.match(subject)
    if not match:
        return None, None, False
    return match.group("type"), match.group("scope"), bool(match.group("breaking"))


def parse_commit_line(raw_hash: str, raw_subject: str) -> Commit:
    commit_type, scope, breaking = _parse_subject(raw_subject)
    section = COMMIT_TYPES.get(commit_type, "Other") if commit_type else "Other"
    return Commit(
        hash=raw_hash[:7],
        subject=raw_subject,
        type=commit_type,
        scope=scope,
        breaking=breaking,
        section=section,
    )


def get_commits(repo_path: str = ".", since: str | None = None) -> list[Commit]:
    """Pull commits from git log, oldest problems (merge noise etc) already
    filtered by --no-merges. `since` can be a tag, branch, or commit hash —
    anything `git log <since>..HEAD` accepts."""
    rev_range = f"{since}..HEAD" if since else "HEAD"
    result = subprocess.run(
        ["git", "log", rev_range, "--no-merges", "--pretty=format:%H\x1f%s"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )

    commits = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        raw_hash, raw_subject = line.split("\x1f", 1)
        commits.append(parse_commit_line(raw_hash, raw_subject))

    return commits
