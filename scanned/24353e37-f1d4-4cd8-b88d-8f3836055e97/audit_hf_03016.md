# [M] User funds lost because they can’t `withdraw

## Summary
Severity: Medium
Contest weight: 0.2109
Dataset id: 16882
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users deposit their funds in `Vault` when epoch is not started but as other users deposit funds too or price of pegged token changes, users get different risk to reward. And they may want to withdraw their funds before epoch start time to get out of bad position, but there is no logic in code to give them ability to withdraw their funds before epoch start time.

## Proof of Concept
`Withdraw()` function in `Vault` only allows users to withdraw after epoch ends and there is no logic in the contract to allow users to withdraw their funds before epoch start time.

After users deposit their funds, the risk to reward ratio of their investment changes as other users deposit funds in one of the Vaults and user may wants to withdraw their funds if they saw that position is bad for them or maybe the price of that token has been changed dramatically before epoch startTime and users wants to withdraw. But, there is no functionality that gives users the ability to withdraw their funds before epoch start time and users lose control of their funds after depositing and before epoch start time. As epoch is not started yet, users should be able to withdraw their funds but there is no such functionality in the code.

## Recommendation
Add some logic to give users the ability to withdraw funds before epoch start time.

Working as intended.
