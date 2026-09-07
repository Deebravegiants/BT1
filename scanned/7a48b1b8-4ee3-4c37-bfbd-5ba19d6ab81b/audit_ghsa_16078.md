# [M] pyspider Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-x4x5-jx9j-mmv7
CVE: CVE-2024-39162
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-11-29
Source: https://github.com/advisories/GHSA-x4x5-jx9j-mmv7
Type: github-advisory

## Affected
- PyPI: `pyspider` — affected >=0

## Details
pyspider through 0.3.10 allows /update XSS. NOTE: This vulnerability only affects products that are no longer supported by the maintainer

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-39162
- https://docs.pyspider.org/en/latest
- https://github.com/binux/pyspider
- https://www.sonarsource.com/blog/basic-http-authentication-risk-uncovering-pyspider-vulnerabilities
