# [M] when rate will be changed for Pool then users

## Summary
Severity: Medium
Contest weight: 0.1155
Dataset id: 20207
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
will pay for all previous epochs accrding to new rate When rate will be changed for Pool then users will pay for all previous epochs accrding to new rate When agent borrows funds from pool, then is should pay interests according to the rate. Currently this rate is minimum(gcred 100), but it can be changed and then gcred of account will be changed and rate will be changed. Once it will be done, that means that user should pay for the previous epochs using this new rate. This is incorrect. Another point, which should be considered is that when agent is liquidated, then penalty rate is used. And again user pays with this penalty rate for all previous epochs, where he was not malicious. This is also incorrect. User pays more fees.

## Recommendation
User should pay for previous epochs according to the previous rates. Same can be said about liquidation and penalty rate.
