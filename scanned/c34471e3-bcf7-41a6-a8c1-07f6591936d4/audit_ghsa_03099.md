# [C] Deserialization of Untrusted Data in bson

## Summary
Severity: Critical
Advisory: GHSA-v8w9-2789-6hhr
CVE: CVE-2020-7610
CWE: CWE-502
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-07
Source: https://github.com/advisories/GHSA-v8w9-2789-6hhr
Type: github-advisory

## Affected
- npm: `bson` — affected >=0 <1.1.4

## Details
All versions of bson before 1.1.4 are vulnerable to Deserialization of Untrusted Data. The package will ignore an unknown value for an object's _bsontype, leading to cases where an object is serialized as a document rather than the intended BSON type.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7610
- https://github.com/mongodb/js-bson/commit/3809c1313a7b2a8001065f0271199df9fa3d16a8
- https://snyk.io/vuln/SNYK-JS-BSON-561052
