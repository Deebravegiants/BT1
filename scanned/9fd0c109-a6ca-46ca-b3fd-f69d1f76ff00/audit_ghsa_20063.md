# [H] rdiffweb vulnerable to Authentication Bypass by Primary Weakness

## Summary
Severity: High
Advisory: GHSA-wf33-6x33-wcf9
CVE: CVE-2022-4722
CWE: CWE-287, CWE-305
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-27
Source: https://github.com/advisories/GHSA-wf33-6x33-wcf9
Type: github-advisory

## Affected
- PyPI: `rdiffweb` — affected >=0 <2.5.5

## Details
In rdiffweb prior to 2.5.5, the username field is not unique to users. This allows exploitation of primary key logic by creating the same name with different combinations & may allow unauthorized access.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4722
- https://github.com/ikus060/rdiffweb/commit/d1aaa96b665a39fba9e98d6054a9de511ba0a837
- https://github.com/ikus060/rdiffweb
- https://github.com/pypa/advisory-database/tree/main/vulns/rdiffweb/PYSEC-2022-43008.yaml
- https://huntr.dev/bounties/c62126dc-d9a6-4d3e-988d-967031876c58
