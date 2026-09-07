# [M] Rebase token, increasing or decreasing, resulting Potential Locked token in `tokenExclusionManager` or Last user unable to `claimRemovedTokens`

## Summary
Severity: Medium
Chain: Smart contract
Component: Velvet-Capital
Published: 2024-06-25
Source: https://github.com/hats-finance/Velvet-Capital-0x0bb0c08fd9eeaf190064f4c66f11d18182961f77/issues/74
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x82e4a38c2e1d252e82f2f6013c9255a290626ee0a8a2fd3a7530a55a244b914a
**Severity:** medium

**Description:**
**Description:**

As from discord message, the `all tokens will be supported` is confirmed by sponsor.

---

In the case of rebasing tokens, which the token balance dynamically can be changed, either increase or decrease in such a time interval, such as `stETH` which increase and recalculates daily, or `OHM`, `AMPL` which can be decreased, this tokens will raise some issues, which can be categorized as 2: The increasing rebase, and decreasing rebase. both have issues.

First, there is a specific behavior to consider when removing a token from the portfolio using `removePortfolioToken`.

When a token is removed via `removePortfolioToken`, it completely removes that token from the portfolio. The balance of the token to be removed is the current total balance held by the vault. This balance is then recorded in the `tokenExclusionManager`, and the token is transferred from the vault to the `tokenExclusionManager`.

The issue arises because the `balanceAtRemoval` might differ from the balance at the time `claimRemovedTokens` is called, particularly for rebasing tokens. 

when the `removePortfolioToken` being called, the `balanceAtRemoval` is set, and being used to calculate on `attemptClaim`. This `balanceAtRemoval` is being used to proportionally related to 'share' of `_portfolioTokenBalance` and `_totalSupply`.

1. Increasing rebase:

some rebasing tokens may remain in the `tokenExclusionManager`, due to `balanceAtRemoval` is less than current balance of rebase token in `tokenExclusionManager` and as there is no function to drain these tokens from the `tokenExclusionManager`, leading to an accumulation of leftover tokens that cannot be transferred.

2. Decreasing rebase:

This decreasing rebase means, `balanceAtRemoval` can be greater than current actual balance of rebase token in `tokenExclusionManager`. This will affect last users, they can't claim, due to decreasing token, meanwhile their balance is still being calculated using old `balanceAtRemoval`, this will result a failed transfer, as the balance in `tokenExclusionManager` is less than their intended claim.

```js
File: Rebalancing.sol
201:   function removePortfolioToken(
202:     address _token
203:   ) external onlyAssetManager nonReentrant {
...
220: @>  uint256 tokenBalance = IERC20Upgradeable(_token).balanceOf(_vault);
221:     _tokenRemoval(_token, tokenBalance);
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Velvet-Capital-0x0bb0c08fd9eeaf190064f4c66f11d18182961f77/issues/74_
