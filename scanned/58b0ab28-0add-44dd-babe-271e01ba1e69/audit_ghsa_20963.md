# [H] rdiffweb Cross-Site Request Forgery vulnerability can lead to user email ID being changed

## Summary
Severity: High
Advisory: GHSA-gmj8-84r4-h46j
CVE: CVE-2022-3274
CWE: CWE-352
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:A/AC:L/PR:L/UI:R/S:U/C:H/I:L/A:H (CVSS_V3)
Published: 2022-09-23
Source: https://github.com/advisories/GHSA-gmj8-84r4-h46j
Type: github-advisory

## Affected
- PyPI: `rdiffweb` — affected >=0 <2.4.7

## Details
rdiffwen prior to version 2.4.7 is vulnerable to Cross-Site Request Forgery (CSRF). An attacker can change a user's email ID. Version 2.4.7 has a fix for this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3274
- https://github.com/ikus060/rdiffweb/commit/e974df75bdbcff3996ad70bd1b4424ec1485ea3f
- https://github.com/ikus060/rdiffweb
- https://github.com/pypa/advisory-database/tree/main/vulns/rdiffweb/PYSEC-2022-289.yaml
- https://huntr.dev/bounties/8834c356-4ddb-4be7-898b-d76f480e9c3f
