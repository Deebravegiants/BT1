# [M] React Router has unexpected external redirect via untrusted paths

## Summary
Severity: Medium
Advisory: GHSA-9jcx-v3wj-wh4m
CVE: CVE-2025-68470
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-01-08
Source: https://github.com/advisories/GHSA-9jcx-v3wj-wh4m
Type: github-advisory

## Affected
- npm: `react-router` — affected >=6.0.0 <6.30.2
- npm: `react-router` — affected >=7.0.0 <7.9.6

## Details
An attacker-supplied path can be crafted so that when a React Router application navigates to it via `navigate()`, `<Link>`, or `redirect()`, the app performs a navigation/redirect to an external URL. This is only an issue if developers pass untrusted content into navigation paths in their application code.

## References
- https://github.com/remix-run/react-router/security/advisories/GHSA-9jcx-v3wj-wh4m
- https://nvd.nist.gov/vuln/detail/CVE-2025-68470
- https://github.com/remix-run/react-router
