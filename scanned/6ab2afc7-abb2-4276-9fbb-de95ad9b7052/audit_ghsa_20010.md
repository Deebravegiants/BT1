# [C] flat vulnerable to Prototype Pollution

## Summary
Severity: Critical
Advisory: GHSA-2j2x-2gpw-g8fm
CVE: CVE-2020-36632
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-25
Source: https://github.com/advisories/GHSA-2j2x-2gpw-g8fm
Type: github-advisory

## Affected
- npm: `flat` — affected >=0 <1.6.2
- npm: `flat` — affected >=2.0.0 <2.0.2
- npm: `flat` — affected >=3.0.0 <3.0.1
- npm: `flat` — affected >=4.0.0 <4.0.2
- npm: `flat` — affected >=5.0.0 <5.0.1

## Details
flat helps flatten/unflatten nested Javascript objects. A vulnerability, which was classified as critical, was found in hughsk flat up to 5.0.0. This affects the function unflatten of the file index.js. The manipulation leads to improperly controlled modification of object prototype attributes ('prototype pollution'). It is possible to initiate the attack remotely. Upgrading to version 5.0.1 can address this issue. The name of the patch is 20ef0ef55dfa028caddaedbcb33efbdb04d18e13. It is recommended to upgrade the affected component. The identifier VDB-216777 was assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36632
- https://github.com/hughsk/flat/issues/105
- https://github.com/hughsk/flat/pull/106
- https://github.com/hughsk/flat/commit/20ef0ef55dfa028caddaedbcb33efbdb04d18e13
- https://github.com/hughsk/flat
- https://github.com/hughsk/flat/compare/3.0.0...3.0.1
- https://github.com/hughsk/flat/compare/4.1.0...4.1.1
- https://github.com/hughsk/flat/compare/v1.6.0...1.6.2
- https://github.com/hughsk/flat/compare/v2.0.1...2.0.2
- https://github.com/hughsk/flat/releases/tag/5.0.1
- https://vuldb.com/?ctiid.216777
- https://vuldb.com/?id.216777
