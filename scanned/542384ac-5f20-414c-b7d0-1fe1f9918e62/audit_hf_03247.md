# [M] ERTR-2 | Weak Referrals

## Summary
Severity: Medium
Contest weight: 0.0773
Dataset id: 17866
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A trader is allowed to specify a different referral code each time an order is created. Only one affiliate is permitted per trader account, so when an order is created with a different affiliate, the affiliate associated with the trader’s account is updated. This can lead to affiliates missing out on rewards if a trader decides to use another affiliate’s referral code even if they were the one to bring the trader onto the platform.

## Recommendation
Consider whether this is desired behavior, if not refactor the referral logic to continue to reward referrers who first bring a trader to the platform.
