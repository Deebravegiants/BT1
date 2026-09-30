# [H] Denial-of-Service Extended Event Loop Blocking in qs

## Summary
Severity: High
Advisory: GHSA-f9cm-p3w6-xvr3
CVE: CVE-2014-10064
CWE: CWE-400
Ecosystem: npm
Published: 2018-10-09
Source: https://github.com/advisories/GHSA-f9cm-p3w6-xvr3
Type: github-advisory

## Affected
- npm: `qs` — affected >=0 <1.0.0

## Details
Versions prior to 1.0.0 of `qs` are affected by a denial of service vulnerability that results from excessive recursion in parsing a deeply nested JSON string.




## Recommendation

Update to version 1.0.0 or later

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-10064
- https://github.com/advisories/GHSA-f9cm-p3w6-xvr3
- https://www.npmjs.com/advisories/28
