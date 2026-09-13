# [M] Regular Expression Denial of Service in path-parse

## Summary
Severity: Medium
Advisory: GHSA-hj48-42vr-x3v9
CVE: CVE-2021-23343
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2021-08-10
Source: https://github.com/advisories/GHSA-hj48-42vr-x3v9
Type: github-advisory

## Affected
- npm: `path-parse` — affected >=0 <1.0.7

## Details
Affected versions of npm package `path-parse` are vulnerable to Regular Expression Denial of Service (ReDoS) via splitDeviceRe, splitTailRe, and splitPathRe regular expressions. ReDoS exhibits polynomial worst-case time complexity.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23343
- https://github.com/jbgutierrez/path-parse/issues/8
- https://github.com/jbgutierrez/path-parse/pull/10
- https://github.com/jbgutierrez/path-parse/commit/eca63a7b9a473bf6978a2f5b7b3343662d1506f7
- https://github.com/jbgutierrez/path-parse
- https://lists.apache.org/thread.html/r6a32cb3eda3b19096ad48ef1e7aa8f26e005f2f63765abb69ce08b85@%3Cdev.myfaces.apache.org%3E
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1279028
- https://snyk.io/vuln/SNYK-JS-PATHPARSE-1077067
