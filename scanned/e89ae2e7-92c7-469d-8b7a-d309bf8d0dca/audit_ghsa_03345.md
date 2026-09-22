# [C] Command injection in spritesheet-js

## Summary
Severity: Critical
Advisory: GHSA-333x-qr3v-g4xx
CVE: CVE-2020-7782
CWE: CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-333x-qr3v-g4xx
Type: github-advisory

## Affected
- npm: `spritesheet-js` — affected >=0

## Details
This affects all versions of package spritesheet-js. It depends on a vulnerable package platform-command. The injection point is located in line 32 in lib/generator.js, which is triggered by main entry of the package.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7782
- https://github.com/krzysztof-o/spritesheet.js/blob/master/lib/generator.js#23L32
- https://snyk.io/vuln/SNYK-JS-SPRITESHEETJS-1048333
- https://www.npmjs.com/package/spritesheet-js
