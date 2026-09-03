# [M] Large dep group requires a lot of resources to process but the cost to commit the transaction is very low.

## Summary
Severity: Medium
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2022-11-02
Source: https://github.com/nervosnetwork/ckb/security/advisories/GHSA-9mfc-chwf-7whf
Type: github-advisory

## Details
### Impact

When a transaction contains a dep group with many cells, the resources required to process it are not linear to the transaction size nor spent script cycles. 

### Patches

In 0.43.3, nodes drop the transactions relayed to them when they contain a dep group with more than 64 cells. They do not ban peers who send them such transactions.

In 0.100, the consensus disallow transactions using a dep group with more than 64 cells. Peers relaying such transaction must be banned. Blocks committing such transactions must be rejected.
