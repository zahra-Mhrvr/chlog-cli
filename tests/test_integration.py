"""
These build an actual git repo in a temp directory and run the real `git
log` subprocess against it, instead of mocking git output. Slower than a
pure unit test, but it's the only way to be sure the subprocess call and
the parser actually agree with each other.
"""

import subprocess

import pytest

from chlog.parser import get_commits
from chlog.changelog import build_changelog


def run(cmd, cwd):
    subprocess.run(cmd, cwd=cwd, check=True, capture_output=True)


@pytest.fixture
def sample_repo(tmp_path):
    repo = tmp_path / "sample_repo"
    repo.mkdir()

    run(["git", "init", "-q"], cwd=repo)
    run(["git", "config", "user.email", "test@example.com"], cwd=repo)
    run(["git", "config", "user.name", "Test User"], cwd=repo)

    commit_messages = [
        "feat: add CSV export",
        "fix(parser): handle trailing whitespace",
        "docs: update install instructions",
        "chore: bump click version",
    ]
    for i, message in enumerate(commit_messages):
        (repo / f"file{i}.txt").write_text("content")
        run(["git", "add", "."], cwd=repo)
        run(["git", "commit", "-q", "-m", message], cwd=repo)

    return repo


def test_get_commits_reads_real_git_log(sample_repo):
    commits = get_commits(str(sample_repo))
    assert len(commits) == 4
    subjects = [c.subject for c in commits]
    assert "feat: add CSV export" in subjects


def test_end_to_end_changelog_from_real_repo(sample_repo):
    commits = get_commits(str(sample_repo))
    changelog = build_changelog(commits, version="v1.0.0")

    assert "### Features" in changelog
    assert "### Bug Fixes" in changelog
    assert "add CSV export" in changelog
    assert "**parser:**" in changelog


def test_since_option_excludes_earlier_commits(sample_repo):
    # tag right after the second commit, then add one more commit after
    run(["git", "tag", "v0.1.0", "HEAD~2"], cwd=sample_repo)
    (sample_repo / "file_extra.txt").write_text("more")
    run(["git", "add", "."], cwd=sample_repo)
    run(["git", "commit", "-q", "-m", "feat: add extra thing"], cwd=sample_repo)

    commits = get_commits(str(sample_repo), since="v0.1.0")
    subjects = [c.subject for c in commits]

    assert "feat: add extra thing" in subjects
    assert "feat: add CSV export" not in subjects
