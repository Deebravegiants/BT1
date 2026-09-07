# [M] Cross-site Scripting in reveal.js

## Summary
Severity: Medium
Advisory: GHSA-6vwx-mwp8-fh44
CVE: CVE-2020-8127
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-05-10
Source: https://github.com/advisories/GHSA-6vwx-mwp8-fh44
Type: github-advisory

## Affected
- npm: `reveal.js` — affected >=0 <3.9.2

## Details
Insufficient validation in cross-origin communication (postMessage) in reveal.js version 3.9.1 and earlier allow attackers to perform cross-site scripting attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8127
- https://hackerone.com/reports/691977
