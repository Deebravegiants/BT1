# [C] BIT-mongoose-2025-23061

## Summary
Severity: Critical
Advisory: BIT-mongoose-2025-23061
Aliases: CVE-2025-23061, GHSA-vg7j-7cwx-8wgw
Ecosystem: Bitnami
Published: 2025-09-25
Source: https://osv.dev/vulnerability/BIT-mongoose-2025-23061
Type: osv

## Affected
- Bitnami: `mongoose` — affected >=8.0.0 <8.9.5

## Details
Mongoose before 8.9.5 can improperly use a nested $where filter with a populate() match, leading to search injection. NOTE: this issue exists because of an incomplete fix for CVE-2024-53900.

## References
- https://github.com/Automattic/mongoose/blob/master/CHANGELOG.md
- https://github.com/Automattic/mongoose/commit/64a9f9706f2428c49e0cfb8e223065acc645f7bc
- https://github.com/Automattic/mongoose/releases/tag/8.9.5
- https://nvd.nist.gov/vuln/detail/CVE-2025-23061
- https://www.npmjs.com/package/mongoose?activeTab=versions
