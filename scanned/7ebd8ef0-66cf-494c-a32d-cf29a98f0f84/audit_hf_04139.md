# [H] GLOBAL-2 | stETH Rebase Frontrunning

## Summary
Severity: High
Contest weight: 0.1860
Dataset id: 20599
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
stETH rebases once a day to reflect the yield earned from staking ETH. This creates issues in the Vault and Issuance contracts. Firstly, in the Vault contract a malicious actor may deposit a different LST, say rETH, before the stETH rebase and withdraw more rETH directly after the stETH rebase -- as the value of the vault has increased by the stETH yield. Secondly, a malicious actor may frontrun the stEth rebase and use the completeWithdrawEarly function in the Issuance contract to buy out a user's stETH pending withdrawal before the rebase is recorded, therefore obtaining the assets at a discount.

## Recommendation
To address the Vault issue, ensure that the withdrawal fee is significant enough to deter make any extraction of the stEth rebase unprofitable. To address the Issuance issue, consider implementing a protocol fee for the buyer of stEth withdrawals such that any value gained from the stEth rebase is overshadowed by the amount paid to the protocol.
