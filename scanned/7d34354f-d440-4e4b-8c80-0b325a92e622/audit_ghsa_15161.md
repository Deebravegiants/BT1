# [H] Path traversal in flaskcode

## Summary
Severity: High
Advisory: GHSA-v3rg-qm46-xrg9
CVE: CVE-2023-52289
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-01-13
Source: https://github.com/advisories/GHSA-v3rg-qm46-xrg9
Type: github-advisory

## Affected
- PyPI: `flaskcode` — affected >=0

## Details
An issue was discovered in the flaskcode package through 0.0.8 for Python. An unauthenticated directory traversal, exploitable with a POST request to a /update-resource-data/<file_path> URI (from views.py), allows attackers to write to arbitrary files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-52289
- https://gitlab.com/daniele_m/cve-list/-/blob/main/README.md
