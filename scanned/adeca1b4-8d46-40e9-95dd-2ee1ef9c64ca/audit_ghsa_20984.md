# [M] rdiffweb vulnerable to Improper Cleanup on Thrown Exception

## Summary
Severity: Medium
Advisory: GHSA-qq29-5vjh-vxwr
CVE: CVE-2022-3301
CWE: CWE-460
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-09-27
Source: https://github.com/advisories/GHSA-qq29-5vjh-vxwr
Type: github-advisory

## Affected
- PyPI: `rdiffweb` — affected >=0 <2.4.8

## Details
rdiffweb prior to version 2.4.8 is vulnerable to Improper Cleanup on Thrown Exception. This could allow an attacker to display a message of their choice onto a web page. Version 2.4.8 contains a fix for this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3301
- https://github.com/ikus060/rdiffweb/commit/5ac38b2a75becbab9f948bd5e37ecbcd9f0b362e
- https://github.com/ikus060/rdiffweb
- https://github.com/pypa/advisory-database/tree/main/vulns/rdiffweb/PYSEC-2022-295.yaml
- https://huntr.dev/bounties/d3bf1e5d-055a-44b8-8d60-54ab966ed63a
