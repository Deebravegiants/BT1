# [M] React Router: Open redirect leading to XSS

## Summary
Severity: Medium
Advisory: GHSA-jjmj-jmhj-qwj2
CVE: CVE-2026-53668
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-07-23
Source: https://github.com/advisories/GHSA-jjmj-jmhj-qwj2
Type: github-advisory

## Affected
- npm: `react-router-dom` — affected >=6.30.2
- npm: `react-router` — affected >=7.9.6 <7.13.0

## Details
Applications with open redirects could permit attacker crafted links to result in redirects to unexpected external location or XSS vectors.

## References
- https://github.com/remix-run/react-router/security/advisories/GHSA-jjmj-jmhj-qwj2
- https://github.com/remix-run/react-router/pull/14718
- https://github.com/remix-run/react-router/commit/3a5b5ad0e5cf9918c646509563f5c41a89226ff3
- https://github.com/remix-run/react-router
- https://github.com/remix-run/react-router/blob/main/CHANGELOG.md#v7180
- https://github.com/remix-run/react-router/releases/tag/react-router@7.18.0
