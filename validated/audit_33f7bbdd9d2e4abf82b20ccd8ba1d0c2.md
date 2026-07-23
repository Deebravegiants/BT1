Audit Report

## Title
`MetricOmmSimpleRouter.metricOmmSwapCallback` Reverts on Zero-Delta Swaps, Breaking Core Swap Flow - (`metric-periphery/contracts/MetricOmmSimpleRouter.sol`)

## Summary

`MetricOmmPool.swap()` unconditionally invokes `metricOmmSwapCallback` on the caller even when `_executeSwap` returns `(0, 0, 0)` — which occurs whenever `priceLimitX64` is already past the current bin price. `MetricOmmSimpleRouter.metricOmmSwapCallback` guards with `if (amount0Delta <= 0 && amount1Delta <= 0) revert InvalidSwapDeltas()`, which fires on `(0, 0)` and reverts the entire swap. The `IMetricOmmSwapCallback` interface explicitly permits both deltas to be zero, so the pool's behavior is correct and the router's guard is the broken invariant.

## Finding Description

**Pool calls callback unconditionally:**

In `MetricOmmPool.swap()`, after `_executeSwap` returns, the callback is invoked with no guard on whether deltas are non-zero: [1](#0-0) [2](#0-1) 

**Early-return paths produce `(0, 0, 0)`:**

`_swapToken0ForToken1SpecifiedInput` returns `(0, 0, 0)` when the price limit is already past the current bin price: [3](#0-2) 

A symmetric early-return exists for the `_swapToken1ForToken0SpecifiedInput` path. After `deltasScaledToExternal`, `amount0Delta = 0` and `amount1Delta = 0`, and the callback is still invoked with `(0, 0, callbackData)`.

**Router rejects `(0, 0)` with a hard revert:** [4](#0-3) 

Since `0 <= 0` is true for both arguments, `InvalidSwapDeltas` is thrown, reverting the entire `swap()` call.

**Interface contract explicitly permits zero deltas:** [5](#0-4) 

## Impact Explanation

All four public swap entry points in `MetricOmmSimpleRouter` — `exactInputSingle`, `exactInput`, `exactOutputSingle`, `exactOutput` — revert with `InvalidSwapDeltas` whenever the pool's swap engine produces zero net deltas. This constitutes broken core swap functionality. The revert is opaque and occurs before the `amountOutMinimum` slippage guard can fire, so callers cannot distinguish a price-limit no-op from a genuine settlement failure. [6](#0-5) 

## Likelihood Explanation

The condition is triggered by normal market operation: any swap submitted with a `priceLimitX64` that the oracle price has already crossed by the time the transaction is mined. No privileged access, malicious setup, or non-standard token is required. This is a routine occurrence on any active pool in volatile markets.

## Recommendation

**Option A (preferred) — Pool skips callback when no settlement is needed:**

Add a guard in `MetricOmmPool.swap()` before invoking the callback:

```solidity
if (amount0Delta != 0 || amount1Delta != 0) {
    uint256 balance0Before = balance0();
    IMetricOmmSwapCallback(msg.sender).metricOmmSwapCallback(amount0Delta, amount1Delta, callbackData);
    if (amount0Delta > 0 && balance0Before + uint256(amount0Delta) > balance0()) {
        revert IncorrectDelta();
    }
}
```

**Option B — Router tolerates zero deltas:**

```solidity
function metricOmmSwapCallback(int256 amount0Delta, int256 amount1Delta, bytes calldata data) external override {
    if (amount0Delta <= 0 && amount1Delta <= 0) return; // no-op swap, nothing to pay
    ...
}
```

## Proof of Concept

1. Deploy a pool with liquidity in bin 0 (current bin).
2. Call `exactInputSingle` through `MetricOmmSimpleRouter` with `zeroForOne = true` and `priceLimitX64` set to a value **above** the current marginal price (already past the ask side).
3. Inside `_swapToken0ForToken1SpecifiedInput`, `params.priceLimitX64 >= initialPriceX64` is true → returns `(0, 0, 0)`.
4. `_executeSwap` returns `amount0Delta = 0`, `amount1Delta = 0`.
5. Pool calls `metricOmmSwapCallback(0, 0, callbackData)` on the router unconditionally.
6. Router fires `if (0 <= 0 && 0 <= 0) revert InvalidSwapDeltas()`.
7. Transaction reverts — swap is unusable for this valid, non-adversarial input. [7](#0-6) [8](#0-7)

### Citations

**File:** metric-core/contracts/MetricOmmPool.sol (L247-263)
```text
    (int256 amount0Delta, int256 amount1Delta, uint256 protocolFeeAmount) =
      _executeSwap(zeroForOne, amountSpecified, params);

    if (zeroForOne) {
      if (amount1Delta < 0) {
        // casting to uint256 is safe because amount1Delta is negative and the ammount of tokens in pool is capped by uint128.max
        // forge-lint: disable-next-line(unsafe-typecast)
        transferToken1(recipient, uint256(-amount1Delta));
      }

      uint256 balance0Before = balance0();
      IMetricOmmSwapCallback(msg.sender).metricOmmSwapCallback(amount0Delta, amount1Delta, callbackData);
      // casting to uint256 is safe because amount0Delta is positive and the ammount of tokens in pool is capped by uint128.max
      // forge-lint: disable-next-line(unsafe-typecast)
      if (amount0Delta > 0 && balance0Before + uint256(amount0Delta) > balance0()) {
        revert IncorrectDelta();
      }
```

**File:** metric-core/contracts/MetricOmmPool.sol (L271-272)
```text
      uint256 balance1Before = balance1();
      IMetricOmmSwapCallback(msg.sender).metricOmmSwapCallback(amount0Delta, amount1Delta, callbackData);
```

**File:** metric-core/contracts/MetricOmmPool.sol (L1148-1150)
```text
      if (params.priceLimitX64 >= initialPriceX64) {
        return (0, 0, 0);
      }
```

**File:** metric-periphery/contracts/MetricOmmSimpleRouter.sol (L46-62)
```text
  function metricOmmSwapCallback(int256 amount0Delta, int256 amount1Delta, bytes calldata data) external override {
    if (amount0Delta <= 0 && amount1Delta <= 0) revert InvalidSwapDeltas();

    _requireExpectedCallbackCaller(msg.sender);

    uint8 callbackMode = _getCallbackMode();

    if (callbackMode == CALLBACK_MODE_JUST_PAY) {
      _justPayCallback(amount0Delta, amount1Delta);
      return;
    }
    if (callbackMode == CALLBACK_MODE_EXACT_OUTPUT_ITERATE) {
      _exactOutputIterateCallback(amount0Delta, amount1Delta, data);
      return;
    }
    revert InvalidCallbackMode(callbackMode);
  }
```

**File:** metric-periphery/contracts/MetricOmmSimpleRouter.sol (L67-86)
```text
  function exactInputSingle(ExactInputSingleParams calldata params) external payable returns (uint256 amountOut) {
    _checkDeadline(params.deadline);
    uint128 priceLimitX64 = MetricOmmSwapPath.normalizePriceLimit(params.zeroForOne, params.priceLimitX64);

    _setNextCallbackContext(params.pool, CALLBACK_MODE_JUST_PAY, msg.sender, params.tokenIn);
    (int128 amount0Delta, int128 amount1Delta) = IMetricOmmPoolActions(params.pool)
      .swap(
        params.recipient,
        params.zeroForOne,
        MetricOmmSwapInputs.asAmountSpecifiedIn(params.amountIn),
        priceLimitX64,
        "",
        params.extensionData
      );
    int128 out = MetricOmmSwapResults.extractAmountOut(params.zeroForOne, amount0Delta, amount1Delta);
    amountOut = MetricOmmSwapInputs.int128ToUint128(out);
    if (amountOut < params.amountOutMinimum) revert InsufficientOutput(amountOut, params.amountOutMinimum);

    _clearExpectedCallbackPool();
  }
```

**File:** metric-core/contracts/interfaces/callbacks/IMetricOmmSwapCallback.sol (L9-9)
```text
///      Both deltas may be zero if no settlement is required for that step.
```
