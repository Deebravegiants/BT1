# [H] glob-parent vulnerable to Regular Expression Denial of Service in enclosure regex

## Summary
Severity: High
Advisory: GHSA-ww39-953v-wcq6
CVE: CVE-2020-28469
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-06-07
Source: https://github.com/advisories/GHSA-ww39-953v-wcq6
Type: github-advisory

## Affected
- npm: `glob-parent` — affected >=4.0.0 <5.1.2

## Details
This affects the package glob-parent before 5.1.2. The enclosure regex used to check for strings ending in enclosure containing path separator.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28469
- https://github.com/gulpjs/glob-parent/pull/36
- https://github.com/gulpjs/glob-parent/pull/36/commits/c6db86422a9731d4f3d332ce4a81c27ea6b0ee46
- https://github.com/gulpjs/glob-parent/commit/4a80667c69355c76a572a5892b0f133c8e1f457e
- https://github.com/gulpjs/glob-parent
- https://github.com/gulpjs/glob-parent/blob/6ce8d11f2f1ed8e80a9526b1dc8cf3aa71f43474/index.js%23L9
- https://github.com/gulpjs/glob-parent/releases/tag/v5.1.2
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWERGITHUBES128-1059093
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1059092
- https://snyk.io/vuln/SNYK-JS-GLOBPARENT-1016905
- https://www.oracle.com/security-alerts/cpujan2022.html
