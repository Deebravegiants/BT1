# [M] CRLF Injection in pypiserver

## Summary
Severity: Medium
Advisory: GHSA-mh24-7wvg-v88g
CVE: CVE-2019-6802
CWE: CWE-74, CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-01-30
Source: https://github.com/advisories/GHSA-mh24-7wvg-v88g
Type: github-advisory

## Affected
- PyPI: `pypiserver` — affected >=0 <1.2.6

## Details
CRLF Injection in pypiserver 1.2.5 and below allows attackers to set arbitrary HTTP headers and possibly conduct XSS attacks via a `%0d%0a` in a URI.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-6802
- https://github.com/pypiserver/pypiserver/issues/237
- https://github.com/pypiserver/pypiserver/commit/1375a67c55a9b8d4619df30d2a1c0b239d7357e6
- https://github.com/pypa/advisory-database/tree/main/vulns/pypiserver/PYSEC-2019-113.yaml
- https://github.com/pypiserver/pypiserver
