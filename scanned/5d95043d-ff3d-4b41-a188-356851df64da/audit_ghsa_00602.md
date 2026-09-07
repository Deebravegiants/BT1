# [M] SimpleMDE XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-wg85-p6j7-gp3w
CVE: CVE-2018-19057
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-11-21
Source: https://github.com/advisories/GHSA-wg85-p6j7-gp3w
Type: github-advisory

## Affected
- npm: `simplemde` — affected >=0

## Details
SimpleMDE 1.11.2 has XSS via an onerror attribute of a crafted IMG element, or via certain input with `[` and `(` characters, which is mishandled during construction of an `A` element.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-19057
- https://github.com/sparksuite/simplemde-markdown-editor/issues/721
- https://github.com/advisories/GHSA-wg85-p6j7-gp3w
- https://github.com/sparksuite/simplemde-markdown-editor
