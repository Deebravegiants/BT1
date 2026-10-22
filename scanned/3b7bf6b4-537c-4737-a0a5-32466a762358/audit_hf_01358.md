# [M] Relayer could lose funds

## Summary
Severity: Medium
Contest weight: 0.0992
Dataset id: 6841
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The xReceive function on the receiver side can contain unreliable code which Relayer is unaware of. In the future, more relayers will participate in completing the transaction.
Consider the following scenario:
1. Say that Relayer A executes the xReceive function on receiver side.
2. In the xReceive function, a call to withdraw function in a foreign contract is made where Relayer A is holding some balance.
3. If this foreign contract is checking tx.origin (say deposit/withdrawal were done via third party), then Relayer A's funds will be withdrawn without his permission (since tx.origin will be the Relayer).

## Recommendation
Relayers should be advised to use an untouched wallet address so that foreign code interaction cannot harm them.
