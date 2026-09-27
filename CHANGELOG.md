## v0.1.0 - 2026-09-27

### Features
- **cli:** add preview and generate commands (`454d299`)
- **changelog:** build keep-a-changelog style markdown from parsed commits (`8fa5021`)
- **parser:** parse conventional commit subjects from git log (`66688d4`)

### Bug Fixes
- **cli:** warn when --prepend is used without --since, was silently duplicating history (`a9c1796`)

### Tests
- add parser, changelog, and real-git-repo integration tests (`69f7840`)

### Other
- Initial commit - project skeleton with packaging config (`069453d`)
