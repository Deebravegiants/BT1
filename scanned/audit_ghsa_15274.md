# [M] Editor.js vulnerable to Code Injection

## Summary
Severity: Medium
Advisory: GHSA-6mvj-2569-3mcm
CVE: CVE-2022-23474
CWE: CWE-79, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-08-05
Source: https://github.com/advisories/GHSA-6mvj-2569-3mcm
Type: github-advisory

## Affected
- npm: `@editorjs/editorjs` — affected >=0 <2.26.0

## Details
Editor.js is a block-style editor with clean JSON output. Versions prior to 2.26.0 are vulnerable to Code Injection via pasted input. The processHTML method passes pasted input into wrapper’s innerHTML. This issue is patched in version 2.26.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-23474
- https://github.com/codex-team/editor.js/pull/2100
- https://github.com/codex-team/editor.js/commit/f659015be6de8e6f0c322c5ff4d1a4532d2f29a2
- https://github.com/codex-team/editor.js
- https://securitylab.github.com/advisories
- https://securitylab.github.com/advisories/GHSL-2022-028_codex-team_editor_js
