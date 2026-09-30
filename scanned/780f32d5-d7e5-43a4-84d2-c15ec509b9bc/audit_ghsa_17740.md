# [M] Indico Insecure Access

## Summary
Severity: Medium
Advisory: GHSA-3wg7-r7q5-r2jf
CVE: CVE-2024-50633
CWE: CWE-201, CWE-639, CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:N (CVSS_V3)
Published: 2025-01-16
Source: https://github.com/advisories/GHSA-3wg7-r7q5-r2jf
Type: github-advisory

## Affected
- PyPI: `indico` — affected >=3.2.9 <3.3.3

## Details
A Broken Object Level Authorization (BOLA) vulnerability in Indico v3.2.9 allows attackers to access sensitive information via sending a crafted POST request to the component /api/principals.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-50633
- https://github.com/cetinpy/CVE-2024-50633/issues/1
- https://github.com/cetinpy/CVE-2024-50633
- https://github.com/indico/indico
