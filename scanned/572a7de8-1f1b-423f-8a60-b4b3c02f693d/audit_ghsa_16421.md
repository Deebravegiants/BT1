# [M] github-slug-action use of `set-env` Runner commands which are processed via stdout

## Summary
Severity: Medium
Advisory: GHSA-7f32-hm4h-w77q
Ecosystem: GitHub Actions
Published: 2024-02-03
Source: https://github.com/advisories/GHSA-7f32-hm4h-w77q
Type: github-advisory

## Affected
- GitHub Actions: `rlespinasse/github-slug-action` — affected >=0 <1.1.1
- GitHub Actions: `rlespinasse/github-slug-action` — affected >=2.0.0 <2.1.1

## Details
### Impact
This GitHub Action use `set-env` runner commands which are processed via stdout related to GHSA-mfwh-5m23-j46w

### Patches
The following versions use the recommended [Environment File Syntax](https://github.com/actions/toolkit/blob/main/docs/commands.md#environment-files).

- 2.1.1
- 1.1.1

### Workarounds
None, it is strongly suggested that you upgrade as soon as possible.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [rlespinasse/github-slug-action](https://github.com/rlespinasse/github-slug-action)

## References
- https://github.com/rlespinasse/github-slug-action/security/advisories/GHSA-7f32-hm4h-w77q
- https://github.com/rlespinasse/github-slug-action
