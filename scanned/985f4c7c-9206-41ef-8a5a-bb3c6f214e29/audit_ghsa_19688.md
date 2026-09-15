# [M] Flask-CORS allows for inconsistent CORS matching

## Summary
Severity: Medium
Advisory: GHSA-8vgw-p6qm-5gr7
CVE: CVE-2024-6844
CWE: CWE-346
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-8vgw-p6qm-5gr7
Type: github-advisory

## Affected
- PyPI: `flask-cors` — affected >=0 <6.0.0

## Details
A vulnerability in corydolphin/flask-cors version 5.0.1 allows for inconsistent CORS matching due to the handling of the '+' character in URL paths. The request.path is passed through the unquote_plus function, which converts the '+' character to a space ' '. This behavior leads to incorrect path normalization, causing potential mismatches in CORS configuration. As a result, endpoints may not be matched correctly to their CORS settings, leading to unexpected CORS policy application. This can cause unauthorized cross-origin access or block valid requests, creating security vulnerabilities and usability issues.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-6844
- https://github.com/corydolphin/flask-cors/commit/35d875319621bd129a38b2b823abf4a2f6cda536
- https://github.com/corydolphin/flask-cors
- https://github.com/corydolphin/flask-cors/blob/main/flask_cors/extension.py#L193
- https://huntr.com/bounties/731a6cd4-d05f-4fe6-8f5b-fe088d7b34e0
- https://lists.debian.org/debian-lts-announce/2025/05/msg00049.html
