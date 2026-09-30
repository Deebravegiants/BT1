# [H] `_calc_min_amount_out` uses manipulable `slot0` price from Uniswap pools instead of an actual TWAP

## Summary
Severity: High
Reporter: WhiteHatMage
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/utils/Univ3Twap.sol#L22
Type: audit-issue

## Details
# `_calc_min_amount_out` uses manipulable `slot0` price from Uniswap pools instead of an actual TWAP

## Summary

`_calc_min_amount_out()` is used by `execute_dca_order()` calculate the minimum amount of tokens expected to get from the swap. That amount is manipulable, making the user that posted the DCA order receive less tokens.

This is because the price taken from the `getSqrtTwapX96()` function in the `Univ3Twap` contract uses `slot0` from the pool, which is the current pool price instead of the TWAP. This can be manipulated by an attacker.

## Vulnerability Detail

The `getSqrtTwapX96()` function in `Univ3Rwap` uses `slot0.sqrtPriceX96`, which is the "The current price of the pool as a sqrt(token1/token0) Q64.96 value" as per Uniswap documentation: https://docs.uniswap.org/contracts/v3/reference/core/interfaces/pool/IUniswapV3PoolState#slot0

The contract name is misleading, as it is actually not the TWAP value.

The function is later used by `getSingleHopTwap()`, and `getTwap()`.

The `Dca` contract consumes the manipulated result from `getTwap()` in `_calc_min_amount_out()` to calculate the minimum amount of tokens to receive from a pool on a swap. If that value is manipulated to be lower, the user will receive less tokens.

DCA orders are first posted by users, and later executed. During the execution in `execute_dca_order()`, that minimum amount is calculated for a swap. An attacker can ultimately use this to perform trades with a manipulated amount.

## Impact

An attacker can manipulate the current price of the pool provided by `slot0` and execute DCA orders from other users at a lower price, making them receive less, and thus lose funds.

## Code Snippet

- https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/utils/Univ3Twap.sol#L22
- https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/utils/Univ3Twap.sol#L53
- https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/utils/Univ3Twap.sol#L66
- https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L268
- https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L213
- https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L220

## Tool used

Manual Review

## Recommendation

Use an actual TWAP oracle instead of the current pool price.
