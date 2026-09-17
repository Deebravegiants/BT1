# [M] Gophish is vulnerable to Incorrect Access Control

## Summary
Severity: Medium
Advisory: GHSA-9f8m-9547-2gqm
CVE: CVE-2025-70963
CWE: CWE-200, CWE-284
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-02-06
Source: https://github.com/advisories/GHSA-9f8m-9547-2gqm
Type: github-advisory

## Affected
- Go: `github.com/gophish/gophish` — affected >=0

## Details
Gophish <= 0.12.1 is vulnerable to Incorrect Access Control. The administrative dashboard exposes each user’s long-lived API key directly inside the rendered HTML/JavaScript of the page on every login. This makes permanent API credentials accessible to any script running in the browser context.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-70963
- https://github.com/gophish/gophish/issues/9366
- https://github.com/gophish/gophish
