# [M] yargs-parser Vulnerable to Prototype Pollution

## Summary
Severity: Medium
Advisory: GHSA-p9pc-299p-vxgp
CVE: CVE-2020-7608
CWE: CWE-1321, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2020-09-04
Source: https://github.com/advisories/GHSA-p9pc-299p-vxgp
Type: github-advisory

## Affected
- npm: `yargs-parser` — affected >=6.0.0 <13.1.2
- npm: `yargs-parser` — affected >=14.0.0 <15.0.1
- npm: `yargs-parser` — affected >=16.0.0 <18.1.1
- npm: `yargs-parser` — affected >=0 <5.0.1

## Details
Affected versions of `yargs-parser` are vulnerable to prototype pollution. Arguments are not properly sanitized, allowing an attacker to modify the prototype of `Object`, causing the addition or modification of an existing property that will exist on all objects.  
Parsing the argument `--foo.__proto__.bar baz'` adds a `bar` property with value `baz` to all objects. This is only exploitable if attackers have control over the arguments being passed to `yargs-parser`.



## Recommendation

Upgrade to versions 13.1.2, 15.0.1, 18.1.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7608
- https://github.com/yargs/yargs-parser/commit/1c417bd0b42b09c475ee881e36d292af4fa2cc36
- https://github.com/yargs/yargs-parser/commit/63810ca1ae1a24b08293a4d971e70e058c7a41e2
- https://github.com/yargs/yargs-parser
- https://snyk.io/vuln/SNYK-JS-YARGSPARSER-560381
- https://www.npmjs.com/advisories/1500
