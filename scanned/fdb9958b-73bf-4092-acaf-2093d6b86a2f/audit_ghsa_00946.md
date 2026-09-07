# [H] Cross-Site Scripting in @toast-ui/editor

## Summary
Severity: High
Advisory: GHSA-cr56-66mx-293v
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-cr56-66mx-293v
Type: github-advisory

## Affected
- npm: `@toast-ui/editor` — affected >=0 <2.2.0

## Details
Versions of `@toast-ui/editor` prior to 2.2.0 are vulnerable to Cross-Site Scripting (XSS).  There are multiple bypasses to the package's built-in XSS sanitization. This may allow attackers to execute arbitrary JavaScript on a victim's browser.

## Recommendation

Upgrade to version 2.2.0 or later.

## References
- https://github.com/nhn/tui.editor/issues/733
- https://github.com/nhn/tui.editor/pull/1010
- https://github.com/nhn/tui.editor/commit/5f62f5eeda9e8f8bcf2075e8e0e10d22bf56d1a7
- https://github.com/nhn/tui.editor
- https://www.npmjs.com/advisories/1521
