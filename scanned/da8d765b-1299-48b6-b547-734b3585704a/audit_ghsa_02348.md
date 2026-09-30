# [C] Process crashes when the cell used as DepGroup is not alive

## Summary
Severity: Critical
Advisory: GHSA-45p7-c959-rgcm
Ecosystem: crates.io
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-45p7-c959-rgcm
Type: github-advisory

## Affected
- crates.io: `ckb` — affected >=0 <0.40.0

## Details
### Impact

It's easy to create a malign transaction which uses the dead cell as the DepGroup in the DepCells. The transaction can crash all the receiving nodes.

## References
- https://github.com/nervosnetwork/ckb/security/advisories/GHSA-45p7-c959-rgcm
- https://rustsec.org/advisories/RUSTSEC-2021-0109.html
