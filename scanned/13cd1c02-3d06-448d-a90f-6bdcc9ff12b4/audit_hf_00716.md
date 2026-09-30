# [M] M-10 | DoS To Keeper Transactions

## Summary
Severity: Medium
Contest weight: 0.1331
Dataset id: 2267
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Market's atomic actions that are not executed with a delay (modifyCollateral and payDebt) can be used to DOS keepers' liquidation calls. Benign keeper who possibly simulated the transaction before executing it and saw that it is executable will see that their orders reverted because a user front-ran the keeper execution. Which in turn keeper will lose gas. Attack Vector: When someone sees a liquidation call for themselves (or ﬂagging), they can front-run this call and either modifyCollateral or payDebt just enough that liquidation call will revert. Although it’s not a problem system-wise considering the trader will be above liquidation threshold in the end, it is an effective way to DOS keepers' liquidation attempts. In the end, user can stay at the liquidation threshold as long as they want and this can lead to fund loss for liquidators for their every liquidation attempt.

## Recommendation
Document this so that keepers can be aware of it and they can use ﬂash-bots to avoid such grieﬁng vectors.
