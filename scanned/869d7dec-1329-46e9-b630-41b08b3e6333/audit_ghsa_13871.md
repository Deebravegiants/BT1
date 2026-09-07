# [M] Path traversal vulnerability in glance

## Summary
Severity: Medium
Advisory: GHSA-3hjh-5hgx-f5wh
CVE: CVE-2022-25937
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-02-13
Source: https://github.com/advisories/GHSA-3hjh-5hgx-f5wh
Type: github-advisory

## Affected
- npm: `glance` — affected >=0 <3.0.9

## Details
Versions of the package glance before 3.0.9 are vulnerable to Directory Traversal that allows users to read files outside the public root directory. This is related to but distinct from the vulnerability reported in [CVE-2018-3715](https://security.snyk.io/vuln/npm:glance:20180129).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25937
- https://github.com/jarofghosts/glance/commit/8cecfe90286e0c45a5494067f1b592d0ccfeabac
- https://gist.github.com/lirantal/c8cfb0398c78e558b7d4ac02aae67809
- https://github.com/jarofghosts/glance
- https://security.snyk.io/vuln/SNYK-JS-GLANCE-3318395
