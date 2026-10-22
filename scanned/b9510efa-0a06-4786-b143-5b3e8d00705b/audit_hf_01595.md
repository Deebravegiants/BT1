# [H] In glAVAX, function _rebalanceWithdraw() withdraws incorrect amount from WAVAX address

## Summary
Severity: High
Contest weight: 0.1847
Dataset id: 8567
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the function _rebalanceWithdraw() if it is necessary to withdraw from WAVAX in order to satisfy a withdrawal, the code will compare the balance of the WAVAX contract and how much is needed to satisfy the withdrawal. When doing this comparison, if it finds that the balance of the WAVAX contract is bigger than how much is needed to satisfy the withdrawal, then it should only withdraw how much it needs. If the opposite happens it should only withdraw the balance in the WAVAX contract. Currently the code does the opposite. Recomendation Change the line in code from: uint256 amountToWithdraw = wavaxBalance > tokenNeeded ? wavaxBalance : tokenNeeded; To: uint256 amountToWithdraw = wavaxBalance > tokenNeeded ? tokenNeeded : wavaxBalance;

## Recommendation
Recommendation not found
