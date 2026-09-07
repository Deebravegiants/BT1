# [M] html-parse-stringify and html-parse-stringify2 vulnerable to Regular expression denial of service (ReDoS)

## Summary
Severity: Medium
Advisory: GHSA-545q-3fg6-48m7
CVE: CVE-2021-23346
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2021-03-18
Source: https://github.com/advisories/GHSA-545q-3fg6-48m7
Type: github-advisory

## Affected
- npm: `html-parse-stringify` — affected >=0 <2.0.1
- npm: `html-parse-stringify2` — affected >=0

## Details
This affects the package html-parse-stringify before 2.0.1; all versions of package html-parse-stringify2. Sending certain input could cause one of the regular expressions that is used for parsing to backtrack, freezing the process.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23346
- https://github.com/HenrikJoreteg/html-parse-stringify/commit/c7274a48e59c92b2b7e906fedf9065159e73fe12
- https://github.com/HenrikJoreteg/html-parse-stringify/blob/master/lib/parse.js%23L2
- https://github.com/HenrikJoreteg/html-parse-stringify/releases/tag/v2.0.1
- https://github.com/rayd/html-parse-stringify2/blob/master/lib/parse.js%23L2
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1080633
- https://snyk.io/vuln/SNYK-JS-HTMLPARSESTRINGIFY-1079306
- https://snyk.io/vuln/SNYK-JS-HTMLPARSESTRINGIFY2-1079307
