# [C] json-pointer vulnerable to Prototype Pollution

## Summary
Severity: Critical
Advisory: GHSA-6xrf-q977-5vgc
CVE: CVE-2022-4742
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-26
Source: https://github.com/advisories/GHSA-6xrf-q977-5vgc
Type: github-advisory

## Affected
- npm: `json-pointer` — affected >=0 <0.6.2

## Details
A vulnerability, which was classified as critical, has been found in json-pointer up to 0.6.1. Affected by this issue is the function set of the file index.js. The manipulation leads to improperly controlled modification of object prototype attributes ('prototype pollution'). The attack may be launched remotely. Upgrading to version 0.6.2 is able to address this issue. The patch is identified as 859c9984b6c407fc2d5a0a7e47c7274daa681941. It is recommended to upgrade the affected component. VDB-216794 is the identifier assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4742
- https://github.com/manuelstofer/json-pointer/pull/36
- https://github.com/manuelstofer/json-pointer/commit/859c9984b6c407fc2d5a0a7e47c7274daa681941
- https://github.com/manuelstofer/json-pointer
- https://vuldb.com/?ctiid.216794
- https://vuldb.com/?id.216794
