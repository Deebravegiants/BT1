# [M] Submit Functions Are Susceptible To Front Running When Trusted Nodes Are Removed

## Summary
Severity: Medium
Contest weight: 0.0922
Dataset id: 14544
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a trusted StaderOracle node is removed using the removeTrustedNode() they should not be able to vote on balances, withdrawals, or beaconStateRoots. However, since the current voting process allows for submissions if the reporting block is >= to the current block.number with no delay period, it is possible for removeTrustedNode() to be front run with a call to (for instance) submitBalances().
Since both transactions can happen in the same block, and submissions do not allow for delay, there is no way to protect against malicious node removal.

## Recommendation
The testing team advises providing a delay before voting begins to ensure malicious entities can’t vote prior to their own removal.
