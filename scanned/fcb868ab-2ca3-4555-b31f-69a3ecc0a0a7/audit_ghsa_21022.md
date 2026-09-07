# [M] rdiffweb CSRF could lead to disabling notifications in user profile

## Summary
Severity: Medium
Advisory: GHSA-9vxf-mcm6-5m42
CVE: CVE-2022-3233
CWE: CWE-352
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-09-22
Source: https://github.com/advisories/GHSA-9vxf-mcm6-5m42
Type: github-advisory

## Affected
- PyPI: `rdiffweb` — affected >=0 <2.4.6

## Details
rdiffweb prior to 2.4.6 is vulnerable to Cross-Site Request Forgery (CSRF), which could lead to disabling notifications in a user's profile.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3233
- https://github.com/ikus060/rdiffweb/commit/18a5aabd48fa6d2d2771a25f95610c28a1a097ca
- https://github.com/ikus060/rdiffweb
- https://github.com/pypa/advisory-database/tree/main/vulns/rdiffweb/PYSEC-2022-285.yaml
- https://huntr.dev/bounties/5ec206e0-eca0-4957-9af4-fdd9185d1db3
