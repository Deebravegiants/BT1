# [H] Path Traversal in Ghost

## Summary
Severity: High
Advisory: GHSA-wf7x-fh6w-34r6
CVE: CVE-2023-32235
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-05-05
Source: https://github.com/advisories/GHSA-wf7x-fh6w-34r6
Type: github-advisory

## Affected
- npm: `ghost` — affected >=0 <5.42.1

## Details
Ghost before 5.42.1 allows remote attackers to read arbitrary files within the active theme's folder via /assets/built%2F..%2F..%2F/ directory traversal. This occurs in frontend/web/middleware/static-theme.js.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-32235
- https://github.com/TryGhost/Ghost/commit/378dd913aa8d0fd0da29b0ffced8884579598b0f
- https://github.com/TryGhost/Ghost
- https://github.com/TryGhost/Ghost/compare/v5.42.0...v5.42.1
