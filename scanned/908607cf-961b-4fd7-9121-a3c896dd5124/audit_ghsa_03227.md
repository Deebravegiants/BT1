# [M] Regular Expression Denial of Service in browserslist

## Summary
Severity: Medium
Advisory: GHSA-w8qv-6jwh-64r5
CVE: CVE-2021-23364
CWE: CWE-1333, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2021-05-24
Source: https://github.com/advisories/GHSA-w8qv-6jwh-64r5
Type: github-advisory

## Affected
- npm: `browserslist` — affected >=4.0.0 <4.16.5

## Details
The package browserslist from 4.0.0 and before 4.16.5 are vulnerable to Regular Expression Denial of Service (ReDoS) during parsing of queries.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23364
- https://github.com/browserslist/browserslist/pull/593
- https://github.com/browserslist/browserslist/commit/c091916910dfe0b5fd61caad96083c6709b02d98
- https://github.com/browserslist/browserslist/blob/e82f32d1d4100d6bc79ea0b6b6a2d281a561e33c/index.js%23L472-L474
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1277182
- https://snyk.io/vuln/SNYK-JS-BROWSERSLIST-1090194
