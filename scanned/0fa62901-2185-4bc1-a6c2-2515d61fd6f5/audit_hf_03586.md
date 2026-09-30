# [M] TRH-3 | Token Rewards DoS

## Summary
Severity: Medium
Contest weight: 0.0805
Dataset id: 19565
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Since the token reward epochs are being pushed into the array on every donation and never removed, there is a risk of DoS because users who supply for the first time will need to go through the entire list of expired epochs for each of the reward tokens present. This will cost users who are supplying to their portfolio for the first time to pay an excessive amount of gas overhead, which may potentially exceed the block gas limit and prevent the user from supplying.

## Recommendation
Consider not going through all past epochs when accruing for a new user and just setting the epoch index to the current one.
