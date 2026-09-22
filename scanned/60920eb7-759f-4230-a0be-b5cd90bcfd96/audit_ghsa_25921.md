# [C] Prototype Pollution in Sails.js

## Summary
Severity: Critical
Advisory: GHSA-8v3j-jfg3-v3fv
CVE: CVE-2021-44908
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-18
Source: https://github.com/advisories/GHSA-8v3j-jfg3-v3fv
Type: github-advisory

## Affected
- npm: `sails` — affected >=0

## Details
Sails.js <= 1.5.2 is vulnerable to Prototype Pollution via controller/load-action-modules.js, function loadActionModules(). A [patch](https://github.com/balderdashy/sails/commit/7c5379a656bb305c958df1dcc2b51a9668830358) is available in the `master` branch of Sails.js's GItHub repository.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-44908
- https://github.com/balderdashy/sails/issues/7209
- https://github.com/balderdashy/sails/commit/7c5379a656bb305c958df1dcc2b51a9668830358
- https://github.com/Marynk/JavaScript-vulnerability-detection/blob/main/sailsJS%20PoC.zip
- https://github.com/balderdashy/sails
- https://github.com/balderdashy/sails/blob/master/lib/app/private/controller/load-action-modules.js#L32
