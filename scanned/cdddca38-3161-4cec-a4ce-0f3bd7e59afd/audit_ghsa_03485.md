# [H] printf vulnerable to Regular Expression Denial of Service (ReDoS)

## Summary
Severity: High
Advisory: GHSA-xfhp-gmh8-r8v2
CVE: CVE-2021-23354
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-03-19
Source: https://github.com/advisories/GHSA-xfhp-gmh8-r8v2
Type: github-advisory

## Affected
- npm: `printf` — affected >=0 <0.6.1

## Details
The package printf before 0.6.1 are vulnerable to Regular Expression Denial of Service (ReDoS) via the regex string 
```regex
/\%(?:\(([\w_.]+)\)|([1-9]\d*)\$)?([0 +\-\]*)(\*|\d+)?(\.)?(\*|\d+)?[hlL]?([\%bscdeEfFgGioOuxX])/g
```
 in `lib/printf.js`. The vulnerable regular expression has cubic worst-case time complexity.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23354
- https://github.com/adaltas/node-printf/issues/31
- https://github.com/adaltas/node-printf/pull/32
- https://github.com/adaltas/node-printf/commit/a8502e7c9b0b22555696a2d8ef67722086413a68
- https://snyk.io/vuln/SNYK-JS-PRINTF-1072096
