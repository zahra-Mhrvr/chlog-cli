from chlog.parser import parse_commit_line


def test_parses_simple_feat_commit():
    commit = parse_commit_line("abc1234", "feat: add dark mode toggle")
    assert commit.type == "feat"
    assert commit.scope is None
    assert commit.section == "Features"
    assert commit.breaking is False


def test_parses_commit_with_scope():
    commit = parse_commit_line("abc1234", "fix(parser): handle empty commit body")
    assert commit.type == "fix"
    assert commit.scope == "parser"
    assert commit.section == "Bug Fixes"


def test_parses_breaking_change_marker():
    commit = parse_commit_line("abc1234", "feat(api)!: drop support for v1 endpoints")
    assert commit.breaking is True
    assert commit.scope == "api"


def test_unknown_type_falls_back_to_other():
    commit = parse_commit_line("abc1234", "wip: still figuring this out")
    assert commit.section == "Other"


def test_non_conventional_subject_falls_back_to_other():
    commit = parse_commit_line("abc1234", "Merge branch 'develop'")
    assert commit.type is None
    assert commit.section == "Other"


def test_hash_is_shortened_to_seven_chars():
    commit = parse_commit_line("abc1234567890", "chore: bump dependencies")
    assert commit.hash == "abc1234"
    assert len(commit.hash) == 7
