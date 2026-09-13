# [M] Flask-CORS improper regex path matching vulnerability

## Summary
Severity: Medium
Advisory: GHSA-7rxf-gvfg-47g4
CVE: CVE-2024-6839
CWE: CWE-41
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-7rxf-gvfg-47g4
Type: github-advisory

## Affected
- PyPI: `flask-cors` — affected >=0 <6.0.0

## Details
corydolphin/flask-cors version 5.0.1 contains an improper regex path matching vulnerability. The plugin prioritizes longer regex patterns over more specific ones when matching paths, which can lead to less restrictive CORS policies being applied to sensitive endpoints. This mismatch in regex pattern priority allows unauthorized cross-origin access to sensitive data or functionality, potentially exposing confidential information and increasing the risk of unauthorized actions by malicious actors.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-6839
- https://github.com/corydolphin/flask-cors/commit/e970988bea563e05e8b8f53fa7bcc134b5bf5c5f
- https://github.com/corydolphin/flask-cors
- https://github.com/corydolphin/flask-cors/blob/4.0.1/flask_cors/core.py#L73
- https://huntr.com/bounties/403eb1fc-86f4-4820-8eba-0f3dfae9f2b4
- https://lists.debian.org/debian-lts-announce/2025/05/msg00049.html
