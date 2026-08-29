# [M] Permit load cell data from memory

## Summary
Severity: Medium
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2021-04-25
Source: https://github.com/nervosnetwork/ckb/security/advisories/GHSA-29c2-65rj-h343
Type: github-advisory

## Details
### Impact

The faulty nodes will reject transactions which calls `load_cell_data` syscall but the input cell is still in the mempool. They also ban other nodes and cause the network separation.

### Patches

0.35.2, 0.36.1, 0.37.1, 0.38.2
