# [M] Authorization Header forwarded on redirect

## Summary
Severity: Medium
Advisory: GHSA-gwvm-45gx-3cf8
CVE: CVE-2018-25091
CWE: CWE-200, CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-10-15
Source: https://github.com/advisories/GHSA-gwvm-45gx-3cf8
Type: github-advisory

## Affected
- PyPI: `urllib3` — affected >=0 <1.24.2

## Details
urllib3 before 1.24.2 does not remove the authorization HTTP header when following a cross-origin redirect (i.e., a redirect that differs in host, port, or scheme). This can allow for credentials in the authorization header to be exposed to unintended hosts or transmitted in cleartext. NOTE: this issue exists because of an incomplete fix for CVE-2018-20060 (which was case-sensitive).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-25091
- https://github.com/urllib3/urllib3/issues/1510
- https://github.com/urllib3/urllib3/commit/adb358f8e06865406d1f05e581a16cbea2136fbc
- https://github.com/pypa/advisory-database/tree/main/vulns/urllib3/PYSEC-2023-207.yaml
- https://github.com/urllib3/urllib3
- https://github.com/urllib3/urllib3/compare/1.24.1...1.24.2
