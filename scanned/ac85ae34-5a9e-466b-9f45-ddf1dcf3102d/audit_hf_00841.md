# [M] M-14 | Rebasing Tokens Are Not Supported

## Summary
Severity: Medium
Contest weight: 0.1126
Dataset id: 2577
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The BasePool uses internal variables to keep track of the pool balance as well as the user's balances and does not use the actual balance of the contract. Therefore rebalance and fee on transfer tokens will not work properly in the system. Here is an example of how a fee on transfer token would act in the system: • User1 deposits 1000 tokens to the pool • User2 deposits 1000 tokens to the pool • User1 withdraws 1000 tokens from the pool • User2 tries to withdraw 1000 tokens from the pool, but the call will revert as the pools balance is lower than 1000 tokens because of the fee on every transfer

## Recommendation
Update the system to support rebasing and fee on transfer tokens, or do not allow them by not setting oracles for these tokens and explicitly state these tokens are not supported.
