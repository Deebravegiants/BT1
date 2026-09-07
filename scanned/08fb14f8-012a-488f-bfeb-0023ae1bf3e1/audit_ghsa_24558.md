# [H] Kallithea Routes CSRF Bypass

## Summary
Severity: High
Advisory: GHSA-799h-qr84-pcrp
CVE: CVE-2016-3691
CWE: CWE-352
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-799h-qr84-pcrp
Type: github-advisory

## Affected
- PyPI: `kallithea` — affected >=0 <0.3.2

## Details
Routes in Kallithea before 0.3.2 allows remote attackers to bypass the CSRF protection by using the GET HTTP request method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-3691
- https://github.com/NexMirror/Kallithea
- http://www.openwall.com/lists/oss-security/2016/05/02/3
