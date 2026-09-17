# [C] Nervos CKB Transaction which calls syscall load_cell_data_hash has nondeterministic result

## Summary
Severity: Critical
Advisory: GHSA-q73f-w3h7-7wcc
Ecosystem: crates.io
Published: 2024-02-03
Source: https://github.com/advisories/GHSA-q73f-w3h7-7wcc
Type: github-advisory

## Affected
- crates.io: `ckb` — affected >=0 <0.34.2

## Details
### Impact
Tx-pool verify transaction which inputs' script contains `load_cell_data_hash` is nondeterministic


### Workarounds
Enforce tx-pool ResolvedTrascation inputs' load data is none.

## References
- https://github.com/nervosnetwork/ckb/security/advisories/GHSA-q73f-w3h7-7wcc
- https://github.com/nervosnetwork/ckb/commit/01eb5b2ecadf7e421b117d6c013e182978746e2f
- https://github.com/nervosnetwork/ckb/commit/fe83220905599e72c97878295f4769e91348d738
- https://github.com/nervosnetwork/ckb/commit/ff88b48779358e038209f3ac1bc1061e6f4deb13
