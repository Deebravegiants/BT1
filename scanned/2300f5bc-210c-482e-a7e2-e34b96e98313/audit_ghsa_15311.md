# [M] CosmWasm wasmd has large address count in ValidateBasic

## Summary
Severity: Medium
Advisory: GHSA-m3rh-cvr5-x6q4
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-08-08
Source: https://github.com/advisories/GHSA-m3rh-cvr5-x6q4
Type: github-advisory

## Affected
- Go: `github.com/CosmWasm/wasmd` — affected >=0 <0.52.0

## Details
**Component:** wasmd
**Criticality:** Low ([ACMv1](https://github.com/interchainio/security/blob/main/resources/CLASSIFICATION_MATRIX.md): I:Moderate; L:Unlikely)
**Patched versions:** wasmd 0.52.0

In multiple wasmd message types it was possible to add a large number of addresses which might lead to unexpected resource consumption in ValidateBasic.

See [CWA-2024-003](https://github.com/CosmWasm/advisories/blob/main/CWAs/CWA-2024-003.md) for more details.

## References
- https://github.com/CosmWasm/wasmd/security/advisories/GHSA-m3rh-cvr5-x6q4
- https://github.com/CosmWasm/wasmd/commit/76c0c061c9cb6b142163883e46c26d99384dc443
- https://github.com/CosmWasm/advisories/blob/main/CWAs/CWA-2024-003.md
- https://github.com/CosmWasm/wasmd
