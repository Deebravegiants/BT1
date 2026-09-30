# [M] Path Traversal in glance

## Summary
Severity: Medium
Advisory: GHSA-2x4q-6jfv-8h9h
CVE: CVE-2018-3715
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-07-26
Source: https://github.com/advisories/GHSA-2x4q-6jfv-8h9h
Type: github-advisory

## Affected
- npm: `glance` — affected >=0 <3.0.4

## Details
Versions of `glance` before 3.0.4 are vulnerable to a Path Traversal vulnerability due to lack of validation of path passed to it, which allows a malicious user to read content of any file with known path.


## Recommendation

Update to version 3.0.4 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3715
- https://github.com/jarofghosts/glance/commit/8cfd88e44ebd3f07e3a2eaf376a3e758b6c4ca19
- https://hackerone.com/reports/310106
- https://github.com/advisories/GHSA-2x4q-6jfv-8h9h
- https://www.npmjs.com/advisories/590
