# [M] UB-4 | Same Winner and Loser

## Summary
Severity: Medium
Contest weight: 0.0846
Dataset id: 16234
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
reportResult does not prevent the oracle from setting the winner and loser to the same side which can lead to loss of funds for many users. Consider a 100 ether bet on one side and 10 ether bet on another, but the 100 ether side is chosen as both the winner and loser. From the calculation in withdrawGain, the contract will attempt to payout a total of 200 ether while it only holds 110. Therefore the users who claim first will deplete the contract and the ones who claim later will experience a complete loss of funds.

## Recommendation
Add a safety check that the arguments _winner and _loser are different.
