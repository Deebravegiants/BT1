# [H] mootools-more vulnerable to prototype pollution

## Summary
Severity: High
Advisory: GHSA-fw45-938v-p26j
CVE: CVE-2021-20088
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-fw45-938v-p26j
Type: github-advisory

## Affected
- npm: `mootools-more` — affected >=0

## Details
Improperly Controlled Modification of Object Prototype Attributes ('Prototype Pollution') in mootools-more 1.6.0 allows a malicious user to inject properties into Object.prototype.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-20088
- https://github.com/BlackFan/client-side-prototype-pollution/blob/master/pp/mootools-more.md
- https://github.com/mootools/mootools-more
