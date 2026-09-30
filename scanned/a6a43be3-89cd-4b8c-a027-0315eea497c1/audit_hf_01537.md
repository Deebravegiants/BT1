# [H] REBALANCER_ROLE can drain funds by rebalancing in a loop in the BorrowingVault

## Summary
Severity: High
Contest weight: 0.1414
Dataset id: 8208
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The rebalancer in the borrowing vault receives a fee for providing debtAsset to repay the originating provider and send to the destination provider. A malicious provider could use this to profit, for example
max fee = 10 / 10000 = 1 / 1000 = 0.001
100_000 debt -> 100_100
100_100 debt -> 100200.1
and so on…
For this attack, the attacker only needs to pay a flashloan fee once (or have the initial funds available).

## Recommendation
The likelihood of this attack is reduced because the rebalancer is a privileged role, but maybe adding a timelock to the rebalancing function would be a good measure so that the chief can disallow a rebalancer if they behave maliciously, before they profit too much from this exploit.
