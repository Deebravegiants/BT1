# [M] Zap contract’s `redeem`

## Summary
Severity: Medium
Contest weight: 0.1197
Dataset id: 1079
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the `redeem()` function, the user can pass a token address. That’s the token they receive in return for the ibbtc they give back. Because of missing address checks the user can provide any possible ERC20 token here without the function reverting.

Although it’s not strictly specified in the code I expect that the user should only be able to redeem wBTC or renBTC tokens since they should also only be able to deposit those.

## Proof of Concept
[`Zap.sol` L216-L238](https://github.com/Badger-Finance/ibbtc/blob/d8b95e8d145eb196ba20033267a9ba43a17be02c/contracts/Zap.sol#L216-L238)

## Recommendation
Verify that the passed token address is either wBTC or renbtc

[tabshaikh (BadgerDAO) disagreed with severity](https://github.com/code-423n4/2021-11-badgerzaps-findings/issues/2#issuecomment-968351408):

best practice to add wBTC or renbtc in require, disagree on the severity

Agree with the finding since only user can rekt themselves I believe this to be a medium severity finding we’ll mitigate by adding a slippage check at the end of the function
