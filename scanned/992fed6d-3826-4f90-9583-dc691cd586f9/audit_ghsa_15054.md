# [H] Path traversal in flaskcode

## Summary
Severity: High
Advisory: GHSA-6h4q-63c5-qfqf
CVE: CVE-2023-52288
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-01-13
Source: https://github.com/advisories/GHSA-6h4q-63c5-qfqf
Type: github-advisory

## Affected
- PyPI: `flaskcode` — affected >=0

## Details
An issue was discovered in the flaskcode package through 0.0.8 for Python. An unauthenticated directory traversal, exploitable with a GET request to a /resource-data/<file_path>.txt URI (from views.py), allows attackers to read arbitrary files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-52288
- https://gitlab.com/daniele_m/cve-list/-/blob/main/README.md
