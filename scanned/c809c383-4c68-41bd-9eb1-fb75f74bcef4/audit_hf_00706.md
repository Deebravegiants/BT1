# [H] H-02 | Split Order May Be Used To Liquidate Accounts

## Summary
Severity: High
Contest weight: 0.1862
Dataset id: 2257
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
An account may be split and it may be put into a state that is immediately liquidatable with liquidateMarginOnly. This is accomplished through the use of accounts with a small position and the use of a small proportion which could result in zero size due to rounding. This attack would result in proﬁts of approximately the amount of the liquidation fee. However, this attack could be repeated many times in the same block and in subsequent blocks until the splitting account was removed from the whitelist. It is because splitAccount is a whitelisted function that this is a High severity rather than a Critical.

## Proof of Concept
https://github.com/GuardianAudits/synthetix-pocs/pull/8/files

## Recommendation
At the end of splitAccount, revert if either the to or from accounts are liquidatable with liquidateMarginOnly.
