# [H] Prototype Pollution in backbone-query-parameters

## Summary
Severity: High
Advisory: GHSA-8qpm-5c82-rf96
CVE: CVE-2021-20085
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-8qpm-5c82-rf96
Type: github-advisory

## Affected
- npm: `backbone-query-parameters` — affected >=0

## Details
Improperly Controlled Modification of Object Prototype Attributes ('Prototype Pollution') in backbone-query-parameters 0.4.0 allows a malicious user to inject properties into Object.prototype.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-20085
- https://github.com/BlackFan/client-side-prototype-pollution/blob/master/pp/backbone-qp.md
