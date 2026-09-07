# [M] `sqrtPriceLimitX96` parameter is hardcoded to `0`

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-opyn
Published: 2022-12-03
Source: https://github.com/sherlock-audit/2022-11-opyn-judging/issues/95
Type: sherlock-finding

## Details
rotcivegaf

medium

# `sqrtPriceLimitX96` parameter is hardcoded to `0`

## Summary

The parameter `sqrtPriceLimitX96` is hardcoded to `0` in functions `depositAuction` and `withdrawAuction` when call `exactInputSingle`

## Vulnerability Detail

According the [UniswapV3 Doc](https://docs.uniswap.org/contracts/v3/guides/swaps/single-swaps):
> sqrtPriceLimitX96: We set this to zero - which makes this parameter inactive. In production, this value can be used to set the limit for the price the swap will push the pool to, which can help protect against price impact or for setting up logic in a variety of price-relevant mechanisms.

`sqrtPriceLimitX96` is basically max slippage you'll allow in the swap. If you're swapping t0 for t1 it needs to be higher than the current `sqrtPriceLimitX96`, lower if you're swapping the other way

## Impact

With `sqrtPriceLimitX96 = 0` may lead to unexpected slippage and subject to sandwich attack

## Code Snippet

- https://github.com/sherlock-audit/2022-11-opyn/blob/main/crab-netting/src/CrabNetting.sol#L527-L537
- https://github.com/sherlock-audit/2022-11-opyn/blob/main/crab-netting/src/CrabNetting.sol#L675-L685

## Tool used

Manual Review

## Recommendation

The Uniswap V3 introduce the concept of centralized liquidity with price range. Setting `sqrtPriceLimitX96` dynamically can help protect against price impact and protect user from unexpected from slippage
Add `sqrtPriceLimitX96` parameter to the `DepositAuctionParams` and `WithdrawAuctionParams` structs, and use in the functions `depositAuction` and `withdrawAuction`:

```diff
@@ -41,6 +41,8 @@ struct DepositAuctionParams {
     uint256 depositsQueued;
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-opyn-judging/issues/95_
