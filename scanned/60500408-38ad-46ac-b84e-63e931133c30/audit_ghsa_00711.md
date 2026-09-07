# [C] Prototype Pollution in ini-parser

## Summary
Severity: Critical
Advisory: GHSA-96r7-mrqf-jhcc
CVE: CVE-2020-7617
CWE: CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-06-10
Source: https://github.com/advisories/GHSA-96r7-mrqf-jhcc
Type: github-advisory

## Affected
- npm: `ini-parser` — affected >=0

## Details
All versions of `ini-parser` are vulnerable to prototype pollution. The `parse` function does not restrict the modification of an Object's prototype, which may allow an attacker to add or modify an existing property that will exist on all objects.




## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7617
- https://github.com/rawiroaisen/node-ini-parser/blob/master/index.js#L14
- https://snyk.io/vuln/SNYK-JS-INIPARSER-564122
- https://www.npmjs.com/advisories/1508
