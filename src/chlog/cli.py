import click

from chlog.changelog import build_changelog
from chlog.parser import get_commits


@click.group()
@click.version_option(package_name="chlog-cli")
def main():
    """Generate a CHANGELOG.md from your git history."""
    pass


@main.command()
@click.option("--repo", default=".", help="Path to the git repo (defaults to current directory)")
@click.option("--since", default=None, help="Only include commits after this tag/ref")
@click.option("--version", "version_label", default=None, help="Label for this changelog entry, e.g. v1.2.0")
def preview(repo, since, version_label):
    """Print the generated changelog to stdout without writing anything."""
    commits = get_commits(repo, since=since)
    click.echo(build_changelog(commits, version=version_label))


@main.command()
@click.option("--repo", default=".", help="Path to the git repo (defaults to current directory)")
@click.option("--since", default=None, help="Only include commits after this tag/ref")
@click.option("--version", "version_label", default=None, help="Label for this changelog entry, e.g. v1.2.0")
@click.option("--output", default="CHANGELOG.md", help="Where to write the changelog")
@click.option("--prepend", is_flag=True, help="Prepend to an existing changelog instead of overwriting it")
def generate(repo, since, version_label, output, prepend):
    """Write the generated changelog to a file."""
    if prepend and not since:
        click.echo(
            "note: --prepend without --since re-includes your whole history "
            "as this entry. Pass --since <last-tag> to only include commits "
            "since your last release.",
            err=True,
        )

    commits = get_commits(repo, since=since)
    new_content = build_changelog(commits, version=version_label)

    if prepend:
        try:
            with open(output, "r") as f:
                existing = f.read()
        except FileNotFoundError:
            existing = ""
        new_content = new_content.rstrip() + "\n\n" + existing

    with open(output, "w") as f:
        f.write(new_content)

    click.echo(f"wrote {len(commits)} commit(s) to {output}")


if __name__ == "__main__":
    main()
