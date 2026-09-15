# [M] Nervos CKB Pool does not remove the conflicting transactions from the statistics 

## Summary
Severity: Medium
Advisory: GHSA-h4c3-5275-vrmg
Ecosystem: crates.io
Published: 2024-02-03
Source: https://github.com/advisories/GHSA-h4c3-5275-vrmg
Type: github-advisory

## Affected
- crates.io: `ckb` — affected >=0 <0.39.2

## Details
### Impact

There's a bug in the pool statistics that when conflicting transactions are removed from the pool, they are not subtracted from the statics. Finally, the transaction pool keeps full and reject all transactions.

### Patches

0.39.2

### Workarounds

Restart the CKB node.

## References
- https://github.com/nervosnetwork/ckb/security/advisories/GHSA-h4c3-5275-vrmg
