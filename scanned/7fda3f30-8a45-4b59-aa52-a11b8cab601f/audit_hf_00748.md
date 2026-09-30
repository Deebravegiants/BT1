# [M] M-12 | USDC Blacklisted Users Can Freeze Market

## Summary
Severity: Medium
Contest weight: 0.0810
Dataset id: 2305
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If the market is disputed or escalated, it could transfer bonds back to the disputor and escalator if
they are not punished. However, since the paymentToken is USDC, which has a blacklist feature, it is
possible for the disputor or escalator is blacklisted when the market attempts to return the bonds.
This would cause the market state transitions to fail. The same issue could occur when attempting to
send rewards to the resolver or disputor if the reward token also has a blacklist feature.

## Recommendation
Consider using the Pull-over-Push pattern when handling bonds and rewards.
