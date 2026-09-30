# [M] WTDU-1 | Users Can Game Withdrawals

## Summary
Severity: Medium
Contest weight: 0.0982
Dataset id: 18185
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A malicious user can front-run the execution of their withdrawal and send their market tokens to another address so that the withdrawal execution fails. The attacker can observe if price moved in their favor between the block where the prices are provided from and the block where their withdrawal execution is happening and decide if they would like their withdrawal to succeed or fail. An attacker can leverage this using the swaps at the end of a withdrawal to capitalize on outdated prices for any assets in the longTokenSwapPath or shortTokenSwapPath.

## Recommendation
Consider transferring the user’s market tokens to a WithdrawalVault upon the withdrawal creation, similar to deposits and orders. Otherwise ensure that the withdrawal fees invalidate any possible risk-free trade that could be made.
