# [M] XSS in apexcharts

## Summary
Severity: Medium
Advisory: GHSA-w46j-8hm6-h8mm
CVE: CVE-2021-23327
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2021-02-11
Source: https://github.com/advisories/GHSA-w46j-8hm6-h8mm
Type: github-advisory

## Affected
- npm: `apexcharts` — affected >=0 <3.24.0

## Details
The package apexcharts before 3.24.0 are vulnerable to Cross-site Scripting (XSS) via lack of sanitization of graph legend fields.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23327
- https://github.com/apexcharts/apexcharts.js/pull/2158
- https://github.com/apexcharts/apexcharts.js/commit/68f3f34d125719b4767614fe0a595cc65bde1d19
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1070616
- https://snyk.io/vuln/SNYK-JS-APEXCHARTS-1062708
- https://www.npmjs.com/package/apexcharts
