### Title
Silent Partial Fill in Exact-Output Swaps When Pool Has Insufficient Tokens — (File: metric-core/contracts/MetricOmmPool.sol)

---

### Summary

`_swapToken1ForToken0SpecifiedOutput` (and its symmetric counterpart `_swapToken0ForToken1SpecifiedOutput`) silently clamps the requested exact-output amount to the pool's available balance instead of reverting. Any caller that invokes `pool.swap()` directly with a negative `amountSpecified` (exact-output mode) will receive a partial fill without any on-chain error, breaking the exact-output invariant at the pool level.

---

### Finding Description

At the entry of `_swapToken1ForToken0SpecifiedOutput`, before the bin-traversal loop, the requested output is unconditionally reduced to whatever the pool currently holds:

```solidity
// metric-core/contracts/MetricOmmPool.sol  ~L872-875
uint256 totalAvailableToken0Scaled = binTotals.scaledToken0;
if (amountOutScaled > totalAvailableToken0Scaled) {
    amountOutScaled = totalAvailableToken0Scaled;   // ← silent clamp, no revert
}
``` [1](#0-0) 

After the clamp, the swap loop runs normally, the callback is invoked, and the pool transfers only the clamped (reduced) amount of token0 to the recipient. The function returns the actual (reduced) deltas; no revert, no dedicated event, and no flag signals that the requested amount was not honoured.

The pool's outer `swap` function then calls the callback and checks only that the caller paid enough input tokens for the *reduced* output — not for the originally requested amount:

```solidity
// metric-core/contracts/MetricOmmPool.sol  ~L271-277
uint256 balance1Before = balance1();
IMetricOmmSwapCallback(msg.sender).metricOmmSwapCallback(amount0Delta, amount1Delta, callbackData);
if (amount1Delta > 0 && balance1Before + uint256(amount1Delta) > balance1()) {
    revert IncorrectDelta();
}
``` [2](#0-1) 

`IncorrectDelta` only guards against the caller *underpaying* for the reduced output; it does not guard against the pool *under-delivering* relative to the original request.

---

### Impact Explanation

Any smart contract or integration that calls `pool.swap()` directly with a negative `amountSpecified` and relies on the exact-output guarantee will silently receive a partial fill. The caller pays fair value for the reduced output (no direct over-charge), but:

1. **Downstream operations fail silently.** If the caller needed exactly N tokens to repay a loan, post collateral, or settle a position, receiving fewer tokens causes those operations to fail or behave incorrectly — after the caller has already spent input tokens.
2. **No revert to signal failure.** The transaction succeeds, so the caller has no automatic protection unless it explicitly compares return values against the requested amount.
3. **The exact-output invariant is broken at the pool level.** The pool advertises an exact-output swap interface (`amountSpecified < 0`) but does not enforce it.

The `MetricOmmSimpleRouter` does add a post-swap check:

```solidity
// metric-periphery/contracts/MetricOmmSimpleRouter.sol  ~L138-139
int128 amountOut = MetricOmmSwapResults.extractAmountOut(...);
if (amountOut != expectedAmountOut) revert InvalidOutputAmount(amountOut, params.amountOut);
``` [3](#0-2) 

This protects router users by reverting the whole transaction. However, the protection lives entirely in the periphery; the pool itself provides no such guarantee, leaving every direct integrator exposed.

---

### Likelihood Explanation

- Any protocol or contract that integrates directly with `MetricOmmPool.swap()` (not through `MetricOmmSimpleRouter`) is affected whenever pool liquidity is insufficient to fill the requested exact-output amount.
- Low-liquidity conditions are normal in oracle-anchored pools (liquidity is concentrated in bins; a large exact-output request can exceed a single bin's balance).
- No privileged access is required; any unprivileged caller can trigger this path.

---

### Recommendation

Add an explicit revert when the pool cannot honour the full exact-output request:

```solidity
uint256 totalAvailableToken0Scaled = binTotals.scaledToken0;
if (amountOutScaled > totalAvailableToken0Scaled) {
    revert InsufficientLiquidity(amountOutScaled, totalAvailableToken0Scaled);
}
```

Apply the same fix symmetrically to `_swapToken0ForToken1SpecifiedOutput`. This aligns the pool's behaviour with the exact-output contract: either deliver the requested amount or revert, never silently deliver less.

---

### Proof of Concept

1. Pool holds `binTotals.scaledToken0 = 500e18` (500 scaled token0 units).
2. Attacker/integrator calls:
   ```solidity
   pool.swap(recipient, /*zeroForOne=*/false, /*amountSpecified=*/-1000, 0, "", "");
   ```
   requesting exactly 1000 token0 out.
3. Inside `_swapToken1ForToken0SpecifiedOutput`, `amountOutScaled` is silently clamped to `500e18`.
4. The swap loop runs, delivering 500 token0 to `recipient`.
5. The callback is invoked; the caller pays token1 for 500 token0 worth of output.
6. `IncorrectDelta` does not fire (caller paid correctly for the reduced amount).
7. `swap()` returns `(amount0Delta, amount1Delta)` reflecting only 500 token0 — the transaction succeeds.
8. The caller expected 1000 token0 and received 500, with no on-chain error. Any downstream operation requiring the full 1000 token0 now fails or is underfunded. [4](#0-3)

### Citations

**File:** metric-core/contracts/MetricOmmPool.sol (L264-278)
```text
    } else {
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
    }
```

**File:** metric-core/contracts/MetricOmmPool.sol (L866-950)
```text
  function _swapToken1ForToken0SpecifiedOutput(uint256 amountOutScaled, SwapMath.InternalSwapParams memory params)
    internal
    returns (uint256, uint256, uint256, uint256)
  {
    unchecked {
      {
        uint256 totalAvailableToken0Scaled = binTotals.scaledToken0;
        if (amountOutScaled > totalAvailableToken0Scaled) {
          amountOutScaled = totalAvailableToken0Scaled;
        }
      }
      (
        BinState memory binState,
        SwapMath.SwapState memory state,
        int256 curBinIdxCache,
        uint256 curPosInBinCache,
        int256 curBinDistE6Cache,
        uint256 lowerPriceX64,
        uint256 upperPriceX64,
        uint256 initialPriceX64
      ) = _getInitialStateForSwap(false, true, params, amountOutScaled);

      if (params.priceLimitX64 <= initialPriceX64) {
        return (0, 0, 0, 0);
      }

      while (state.amountSpecifiedRemainingScaled > 0) {
        bool nonEmptyBin = true;
        if (binState.token0BalanceScaled == 0 || curPosInBinCache >= type(uint104).max) {
          if (params.priceLimitX64 <= upperPriceX64) {
            break;
          }
          nonEmptyBin = false;
        }

        if (nonEmptyBin) {
          int256 delta0Scaled;
          int256 delta1Scaled;
          uint256 binLpFeeAmountScaled;

          (curPosInBinCache, delta0Scaled, delta1Scaled, binLpFeeAmountScaled) = SwapMath.buyToken0InBinSpecifiedOut(
            binState,
            curPosInBinCache,
            state,
            params.baseFeeX64 + Math.mulDiv(binState.addFeeBuyE6, ONE_X64, 1e6),
            lowerPriceX64,
            upperPriceX64,
            params.priceLimitX64,
            spreadFeeE6
          );

          emit BinSwapped(
            curBinIdxCache,
            BinBalanceDelta({delta0Scaled: delta0Scaled, delta1Scaled: delta1Scaled}),
            binLpFeeAmountScaled
          );
          _saveBinState(curBinIdxCache, binState);
        }

        if (curPosInBinCache >= type(uint104).max || !nonEmptyBin) {
          if (curBinIdxCache >= HIGHEST_BIN) {
            break;
          }
          curBinIdxCache++;
          curPosInBinCache = 0;
          curBinDistE6Cache = _clampInt256ToInt24(_addDistE6(int256(curBinDistE6Cache), binState.lengthE6));

          lowerPriceX64 = upperPriceX64;
          binState = _binStates[curBinIdxCache];
          upperPriceX64 = distanceE6ToPriceX64(_addDistE6(curBinDistE6Cache, binState.lengthE6), params.midPriceX64);
        } else {
          break;
        }
      }

      _finalizeSwap(curBinIdxCache, curPosInBinCache, curBinDistE6Cache);

      return (
        state.amountCalculatedScaled,
        amountOutScaled - state.amountSpecifiedRemainingScaled,
        state.protocolFeeAmountScaled,
        state.feeExclusiveInputScaled
      );
    }
  }
```

**File:** metric-periphery/contracts/MetricOmmSimpleRouter.sol (L138-139)
```text
    int128 amountOut = MetricOmmSwapResults.extractAmountOut(params.zeroForOne, amount0Delta, amount1Delta);
    if (amountOut != expectedAmountOut) revert InvalidOutputAmount(amountOut, params.amountOut);
```
