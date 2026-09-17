# [M] Path Traversal in droppy

## Summary
Severity: Medium
Advisory: GHSA-grv5-w5vr-8h98
CVE: CVE-2020-7757
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-05-10
Source: https://github.com/advisories/GHSA-grv5-w5vr-8h98
Type: github-advisory

## Affected
- npm: `droppy` — affected >=0

## Details
This affects all versions of package droppy. It is possible to traverse directories to fetch configuration files from a droopy server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7757
- https://github.com/silverwind/droppy/blob/master/server/server.js%23L845
- https://snyk.io/vuln/SNYK-JS-DROPPY-1023656
