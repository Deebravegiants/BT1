# [M] Check on `MAX_TOTAL_TOKEN_NUMBER` off by one

## Summary
Severity: Medium
Chain: Smart contract
Component: Wise-Lending
Published: 2024-02-16
Source: https://github.com/hats-finance/Wise-Lending-0xa2ca45d6e249641e595d50d1d9c69c9e3cd22573/issues/39
Type: hats-finding

## Details
**Github username:** @bahurum
**Twitter username:** bahurum
**Submission hash (on-chain):** 0xeb9b01b0239038e2046821da7520c0f0ce211ee751d1d0394967435e36c2d3ed
**Severity:** medium

**Description:**
**Description**

*Note that this is actually a low level severity issue.*

The check in [`MainHelper.sol`](https://github.com/wise-foundation/lending-audit/blob/1637d6e455e81712b9b23c7f3ae80149d9631a35/contracts/MainHelper.sol#L636) on the number of tokens deposited is off by one, meaning that instead of allowing to deposit `MAX_TOTAL_TOKEN_NUMBER` tokens, it allows `MAX_TOTAL_TOKEN_NUMBER + 1` tokens.

**Recommendation**\
Consider the following change:
```diff
    ...
-   if (userTokenData[_nftId].length > MAX_TOTAL_TOKEN_NUMBER) {
+   if (userTokenData[_nftId].length >= MAX_TOTAL_TOKEN_NUMBER) {
        revert TooManyTokens();
    }
    ...
```
