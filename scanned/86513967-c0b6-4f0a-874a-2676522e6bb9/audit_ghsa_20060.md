# [C] replicator vulnerable to Deserialization of Untrusted Data

## Summary
Severity: Critical
Advisory: GHSA-hw46-vg6w-88fj
CVE: CVE-2021-33420
CWE: CWE-502
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-15
Source: https://github.com/advisories/GHSA-hw46-vg6w-88fj
Type: github-advisory

## Affected
- npm: `replicator` — affected >=0 <1.0.4

## Details
A deserialization issue discovered in inikulin replicator before 1.0.4 allows remote attackers to run arbitrary code via the fromSerializable function in TypedArray object.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-33420
- https://github.com/inikulin/replicator/issues/16
- https://github.com/inikulin/replicator/pull/17
- https://github.com/inikulin/replicator/commit/2c626242fb4a118855262c64b5731b2ce98e521b
- https://advisory.checkmarx.net/advisory/CX-2021-4787
- https://github.com/inikulin/replicator
