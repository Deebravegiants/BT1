# [H] `UniV3Vault.sol#collectEarnings`

## Summary
Severity: High
Contest weight: 0.1771
Dataset id: 1301
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
For `UniV3Vault`, it seems that lp fees are collected through `collectEarnings()` callable by the `strategy` and reinvested (rebalanced).

However, in the current implementation, unharvested yields are not included in `tvl()`, making it vulnerable to front-run attacks that steal pending yields.

  * <https://github.com/code-423n4/2021-12-mellow/blob/6679e2dd118b33481ee81ad013ece4ea723327b5/mellow-vaults/contracts/UniV3Vault.sol#L100-L122>
  * <https://github.com/code-423n4/2021-12-mellow/blob/6679e2dd118b33481ee81ad013ece4ea723327b5/mellow-vaults/contracts/UniV3Vault.sol#L80-L97>

## Recommendation
Consider including fees in `tvl()`.

For the code to calculate fees earned, please reference `_computeFeesEarned()` in G-UNI project:

  * <https://github.com/gelatodigital/g-uni-v1-core/blob/master/contracts/GUniPool.sol#L762-L806>

Thanks! Added `tokensOwed` to `UniV3Vault`’s `tvl`
