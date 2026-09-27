from chlog.parser import Commit
from chlog.changelog import build_changelog, group_by_section


def make_commit(section, subject="did a thing", scope=None, breaking=False, hash="abc1234"):
    return Commit(hash=hash, subject=subject, type=None, scope=scope, breaking=breaking, section=section)


def test_groups_commits_by_section():
    commits = [
        make_commit("Features", "add search"),
        make_commit("Bug Fixes", "fix crash"),
        make_commit("Features", "add filters"),
    ]
    groups = group_by_section(commits)
    assert len(groups["Features"]) == 2
    assert len(groups["Bug Fixes"]) == 1


def test_empty_commit_list_says_no_changes():
    result = build_changelog([])
    assert "no changes" in result.lower()


def test_features_section_appears_before_bug_fixes():
    commits = [make_commit("Bug Fixes"), make_commit("Features")]
    result = build_changelog(commits)
    assert result.index("### Features") < result.index("### Bug Fixes")


def test_scope_is_bolded_in_output():
    commits = [make_commit("Features", subject="feat(auth): add login", scope="auth")]
    result = build_changelog(commits)
    assert "**auth:**" in result


def test_breaking_change_gets_flagged():
    commits = [make_commit("Features", breaking=True)]
    result = build_changelog(commits)
    assert "BREAKING" in result


def test_version_label_shows_up_in_header():
    commits = [make_commit("Features")]
    result = build_changelog(commits, version="v2.0.0")
    assert result.startswith("## v2.0.0")


def test_no_version_label_defaults_to_unreleased():
    commits = [make_commit("Features")]
    result = build_changelog(commits)
    assert result.startswith("## Unreleased")
