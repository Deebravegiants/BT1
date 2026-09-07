# [?] fix(test): keep temporary test data on panic (#5272)

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2026-07-06
Source: https://github.com/nervosnetwork/ckb/commit/fe5f4962a6f6d2f04f73f653f51cc61e392ef56d
Type: security-commit

## Details
fix(test): keep temporary test data on panic (#5272)

<!--
Thank you for contributing to nervosnetwork/ckb!

If you haven't already, please read
[CONTRIBUTING](https://github.com/nervosnetwork/ckb/blob/develop/CONTRIBUTING.md)
document.

If you're unsure about anything, just ask; somebody should be along to
answer within a day or two.

**Important**: We use Squash Merge to merge PRs, so the PR title will
become the commit message.
Please ensure your PR title follows the [Conventional Commit
Messages](https://www.conventionalcommits.org/) format.

The most important prefixes you should use:

- `fix:`: represents bug fixes, and results in a SemVer patch bump.
- `feat:`: represents a new feature, and results in a SemVer minor bump.
- `<prefix>!:` (e.g. `feat!:`): represents a breaking change (indicated
by the !) and results in a SemVer major bump.

Other conventional prefixes are also acceptable (e.g., `docs:`,
`refactor:`, `test:`, `chore:`, etc.).
-->
### What problem does this PR solve?

Problem Summary:

When running `ckb-test` with `--keep-tmp-data`, temporary node
directories are still deleted when a spec panics or errors. This makes
it hard to inspect logs and state after a failed test run.

### What is changed and how it works?

When `clean_tmp` is false, call `std::mem::forget(path)` to prevent

_Trimmed to 38 lines — full report: https://github.com/nervosnetwork/ckb/commit/fe5f4962a6f6d2f04f73f653f51cc61e392ef56d_
