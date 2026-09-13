# [M] Pool does not remove the conflicting transactions from the statistics. Finally the pool is full and reject all transactions.

## Summary
Severity: Medium
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2021-03-10
Source: https://github.com/nervosnetwork/ckb/security/advisories/GHSA-h4c3-5275-vrmg
Type: github-advisory

## Details
### Impact

There's a bug in the pool statistics that when conflicting transactions are removed from the pool, they are not subtracted from the statics. Finally, the transaction pool keeps full and reject all transactions.

### Patches

0.39.2

### Workarounds

Restart the CKB node.
