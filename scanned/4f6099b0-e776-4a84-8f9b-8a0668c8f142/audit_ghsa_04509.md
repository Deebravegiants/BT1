# [H] pdfkit: Path traversal in from_string

## Summary
Severity: High
Advisory: GHSA-9g3x-6x24-vf9f
CVE: CVE-2025-26240
CWE: CWE-120, CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-9g3x-6x24-vf9f
Type: github-advisory

## Affected
- PyPI: `pdfkit` — affected >=0

## Details
In JazzCore python-pdfkit 1.0.0, the from_string method enables the execution of JavaScript code within the context of the server application and the exfiltration of local files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-26240
- https://github.com/JazzCore/python-pdfkit
- https://habuon.github.io/2025/03/12/pdfkit-vulnerability-%28CVE-2025-26240%29.html
- https://www.csirt.gov.sk/the-python-pdfkit-library-vulnerability.html
