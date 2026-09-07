# [M] rdiffweb CSRF vulnerability in admin area can lead to deletion of repositories and users

## Summary
Severity: Medium
Advisory: GHSA-cw2v-wv4g-w4p6
CVE: CVE-2022-3232
CWE: CWE-352
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-09-18
Source: https://github.com/advisories/GHSA-cw2v-wv4g-w4p6
Type: github-advisory

## Affected
- PyPI: `rdiffweb` — affected >=0 <2.4.5

## Details
rdiffweb prior to 2.4.5 is vulnerable to Cross-Site Request Forgery (CSRF). An attacker exploiting this vulnerability can use it to delete repositories and users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3232
- https://github.com/ikus060/rdiffweb/commit/422791ea45713aaaa865bdca74addb9fffd93a71
- https://github.com/ikus060/rdiffweb
- https://github.com/pypa/advisory-database/tree/main/vulns/rdiffweb/PYSEC-2022-281.yaml
- https://huntr.dev/bounties/15c8fd98-7f50-4d46-b013-42710af1f99c
