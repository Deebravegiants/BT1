# [H] CKAN contains Improper Authentication leading to account takeover

## Summary
Severity: High
Advisory: GHSA-m2xp-jxfg-qq6g
CVE: CVE-2022-43685
CWE: CWE-287, CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-11-22
Source: https://github.com/advisories/GHSA-m2xp-jxfg-qq6g
Type: github-advisory

## Affected
- PyPI: `ckan` — affected >=0 <2.9.7

## Details
CKAN through 2.9.6 account takeovers by unauthenticated users when an existing user id is sent via an HTTP POST request. This allows a user to take over an existing account including superuser accounts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-43685
- https://ckan.org
- https://ckan.org/blog/get-latest-patch-releases-your-ckan-site-october-2022
- https://github.com/ckan/ckan
- https://github.com/pypa/advisory-database/tree/main/vulns/ckan/PYSEC-2022-42987.yaml
