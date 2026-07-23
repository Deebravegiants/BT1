Audit Report

## Title
Exact-Output Swap Silently Delivers Zero Tokens Instead of Reverting on Insufficient Liquidity — (`metric-core/contracts/MetricOmmPool.sol`)

## Summary
Both `_swapToken1ForToken0SpecifiedOutput` and `_swapToken0ForToken1SpecifiedOutput` unconditionally clamp the requested output to the pool's available balance before the swap loop, including clamping to zero when the pool is empty. When clamped to zero, the loop never executes, both deltas return as zero, no tokens are transferred, and the transaction succeeds silently — violating the exact-out invariant that callers must receive exactly the requested amount or the call reverts.

## Finding Description
In `_swapToken1ForToken0SpecifiedOutput`, the requested output is silently capped before the swap loop:

```solidity
// L872-875
uint256 totalAvailableToken0Scaled = binTotals.scaledToken0;
if (amountOutScaled > totalAvailableToken0Scaled) {
    amountOutScaled = totalAvailableToken0Scaled;   // silent cap — no revert
}
``` [1](#0-0) 

When `totalAvailableToken0Scaled == 0`, `amountOutScaled` becomes `0`. `_getInitialStateForSwap` initializes `state.amountSpecifiedRemainingScaled = amountOutScaled = 0`, so the `while (state.amountSpecifiedRemainingScaled > 0)` loop at L892 never executes. The function returns `(0, 0, 0, 0)`. [2](#0-1) 

Back in `_executeSwap`, both scaled deltas are set to zero: [3](#0-2) 

In `swap()`, since `amount0Delta == 0`, no token is transferred to the recipient. The callback is invoked with `(0, 0)`. The `IncorrectDelta` guard at L275 checks `amount1Delta > 0` — since it is `0`, the guard is skipped and the transaction completes successfully. [4](#0-3) 

The symmetric path `_swapToken0ForToken1SpecifiedOutput` follows the identical pattern: [5](#0-4) 

There is no post-loop check comparing actual output delivered against the originally requested amount. A search for `InsufficientLiquidity` confirms the error is defined in `IMetricOmmPoolActions.sol` and used in `LiquidityLib.sol` but is never raised in the swap path of `MetricOmmPool.sol`.

## Impact Explanation
This breaks the core exact-out swap invariant. Routers and aggregators that call `swap` with `amountSpecified < 0` expecting to receive a precise output amount will silently receive zero tokens while paying zero input. If such a router has already committed to delivering tokens to an end user (e.g., a multi-hop aggregator), the router itself suffers a fund shortfall. The `priceLimitX64` slippage guard does not protect against this because price does not move when no swap executes — the guard is entirely bypassed. This constitutes broken core pool swap functionality with potential for fund loss at the router/aggregator layer, meeting the contest's "Broken core pool functionality causing loss of funds or unusable swap flows" criterion.

## Likelihood Explanation
Any caller submitting an exact-out swap against a pool whose relevant bin liquidity has been drained — by a concurrent swap, a front-runner, or natural trading — triggers this silently. No special privilege is required. An attacker can deliberately front-run a pending exact-out swap by draining the relevant token balance via a normal exact-in swap, causing the victim's transaction to produce `(0, 0)` deltas, then back-run to restore liquidity at a profit. The attack is repeatable by any EOA or contract that can call `swap`.

## Recommendation
After the swap loop completes in both `_swapToken1ForToken0SpecifiedOutput` and `_swapToken0ForToken1SpecifiedOutput`, compare the actual output delivered against the originally requested amount and revert if the pool could not fill the order:

```solidity
uint256 actualOut = amountOutScaled - state.amountSpecifiedRemainingScaled;
if (actualOut < requestedAmountOutScaled) revert InsufficientLiquidity();
```

The `requestedAmountOutScaled` must be captured before the silent-cap block. Alternatively, remove the silent cap entirely and let the loop exhaust available liquidity, then revert if `state.amountSpecifiedRemainingScaled > 0` after the loop.

## Proof of Concept

```solidity
// 1. Attacker drains all token0 from the pool via a normal exact-in swap.
pool.swap(attacker, false /*token1→token0*/, type(int128).max, 0, ...);

// 2. Victim submits exact-out swap requesting 1 000 token0.
//    amountSpecified = -1000e18 (exact out, !zeroForOne)
(int128 d0, int128 d1) = pool.swap(victim, false, -1000e18, 0, ...);
// d0 == 0, d1 == 0 — victim receives nothing, pays nothing, tx succeeds silently.
// A Swap event is emitted with zero amounts. No revert, no slippage error.

// 3. Attacker back-runs: re-adds or re-buys liquidity at the shifted price.
```

A Foundry test can verify this by: (a) deploying a pool with known liquidity, (b) calling `swap` with `type(int128).max` exact-in to drain token0, (c) calling `swap` with `amountSpecified = -1e18` exact-out and asserting `d0 == 0 && d1 == 0` while the call does not revert.

### Citations

**File:** metric-core/contracts/MetricOmmPool.sol (L265-277)
```text
      if (amount0Delta < 0) {
        // casting to uint256 is safe because amount0Delta is negative and the ammount of tokens in pool is capped by uint128.max
        // forge-lint: disable-next-line(unsafe-typecast)
        transferToken0(recipient, uint256(-amount0Delta));
      }

      uint256 balance1Before = balance1();
      IMetricOmmSwapCallback(msg.sender).metricOmmSwapCallback(amount0Delta, amount1Delta, callbackData);
      // casting to uint256 is safe because amount1Delta is positive and the ammount of tokens in pool is capped by uint128.max
      // forge-lint: disable-next-line(unsafe-typecast)
      if (amount1Delta > 0 && balance1Before + uint256(amount1Delta) > balance1()) {
        revert IncorrectDelta();
      }
```

**File:** metric-core/contracts/MetricOmmPool.sol (L700-703)
```text
          // forge-lint: disable-next-line(unsafe-typecast)
          amount0DeltaScaled = -int256(amountOutScaled);
          // forge-lint: disable-next-line(unsafe-typecast)
          amount1DeltaScaled = int256(amountInScaled);
```

**File:** metric-core/contracts/MetricOmmPool.sol (L872-875)
```text
        uint256 totalAvailableToken0Scaled = binTotals.scaledToken0;
        if (amountOutScaled > totalAvailableToken0Scaled) {
          amountOutScaled = totalAvailableToken0Scaled;
        }
```

**File:** metric-core/contracts/MetricOmmPool.sol (L892-892)
```text
      while (state.amountSpecifiedRemainingScaled > 0) {
```

**File:** metric-core/contracts/MetricOmmPool.sol (L1048-1052)
```text
      {
        uint256 totalAvailableToken1Scaled = binTotals.scaledToken1;
        if (amountOutScaled > totalAvailableToken1Scaled) {
          amountOutScaled = totalAvailableToken1Scaled;
        }
```
