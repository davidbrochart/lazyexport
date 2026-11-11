Changelog fragments
===================

Add a brief user-facing summary to <issue-or-PR-number>.<type>.rst.
Supported types: added, changed, fixed, removed.
For changes without an issue or PR, use +description.<type>.rst.
Do not include issue links or author credits in the fragment text.
Preview with: uv run --group dev towncrier build --draft --version 0.1.0
Build the changelog before tagging a release, then commit the generated
CHANGELOG.rst and the removal of consumed fragments.
