Audit Report

## Title
`MetricOmmSimpleRouter.metricOmmSwapCallback` Reverts on Zero-Delta Swaps, Breaking Core Swap Flow - (File: `metric-periphery/contracts/MetricOmmSimpleRouter.sol`)

## Summary

`MetricOmmPool.swap()` unconditionally invokes `metricOmmSwapCallback` on the caller even when the swap engine returns `(0, 0, 0)` net deltas. `MetricOmmSimpleRouter.metricOmmSwapCallback` guards against this with `if (amount0Delta <= 0 && amount1Delta <= 0) revert InvalidSwapDeltas()`, which fires on `(0, 0)` and reverts the entire swap transaction. The `IMetricOmmSwapCallback` interface explicitly documents that both deltas may be zero, making the router's guard a broken invariant.

## Finding Description

**Pool calls callback unconditionally:**

In `MetricOmmPool.swap()`, after `_executeSwap` returns, the callback is invoked with no guard on whether deltas are non-zero: [1](#0-0) [2](#0-1) 

**Swap engine early-return paths produce `(0, 0, 0)`:**

`_swapToken0ForToken1SpecifiedInput` returns `(0, 0, 0)` when `priceLimitX64` is already at or above the current price: [3](#0-2) 

The symmetric path in `_swapToken1ForToken0SpecifiedInput` does the same when `priceLimitX64 <= initialPriceX64`. After `deltasScaledToExternal`, `amount0Delta = 0` and `amount1Delta = 0`, and the callback is still invoked with `(0, 0, callbackData)`.

**Router rejects `(0, 0)` deltas:** [4](#0-3) 

Since `0 <= 0` is true for both arguments, `InvalidSwapDeltas` is thrown, reverting the entire `swap()` call.

**Interface contract violated:**

The `IMetricOmmSwapCallback` NatSpec explicitly permits zero deltas: [5](#0-4) 

The router violates this documented contract.

## Impact Explanation

Any swap routed through `MetricOmmSimpleRouter` — `exactInputSingle`, `exactInput`, `exactOutputSingle`, `exactOutput` — reverts with `InvalidSwapDeltas` whenever the pool's swap engine produces zero net deltas. This includes swaps submitted with a `priceLimitX64` that the oracle price has already crossed by the time the transaction is mined, and pools whose active bin has been fully drained with the price limit preventing crossing into the next bin. The revert is opaque and occurs before the `amountOutMinimum` slippage guard can fire, making core swap functionality through the only production router broken for a reachable, non-adversarial input class. This constitutes broken core pool functionality causing an unusable swap flow.

## Likelihood Explanation

The condition is triggered by normal market operation: any swap submitted with a `priceLimitX64` that the oracle price crosses between transaction submission and inclusion. No privileged access, malicious setup, or non-standard token is required. This is a routine occurrence on any active pool in volatile markets.

## Recommendation

**Option A — Pool skips callback when no settlement is needed (preferred):**

In `MetricOmmPool.swap()`, guard the callback invocation:

```solidity
if (amount0Delta > 0 || amount1Delta != 0) {
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

1. Deploy a pool with liquidity in the active bin.
2. Call `exactInputSingle` through `MetricOmmSimpleRouter` with `zeroForOne = true` and `priceLimitX64` set to a value at or above the current marginal price.
3. Inside `_swapToken0ForToken1SpecifiedInput`, `params.priceLimitX64 >= initialPriceX64` is true → returns `(0, 0, 0)`.
4. `_executeSwap` returns `amount0Delta = 0`, `amount1Delta = 0`.
5. Pool calls `metricOmmSwapCallback(0, 0, callbackData)` on the router unconditionally.
6. Router fires `if (0 <= 0 && 0 <= 0) revert InvalidSwapDeltas()`.
7. Transaction reverts — swap is unusable for this valid, non-adversarial input.

### Citations

**File:** metric-core/contracts/MetricOmmPool.sol (L257-258)
```text
      uint256 balance0Before = balance0();
      IMetricOmmSwapCallback(msg.sender).metricOmmSwapCallback(amount0Delta, amount1Delta, callbackData);
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

**File:** metric-periphery/contracts/MetricOmmSimpleRouter.sol (L46-48)
```text
  function metricOmmSwapCallback(int256 amount0Delta, int256 amount1Delta, bytes calldata data) external override {
    if (amount0Delta <= 0 && amount1Delta <= 0) revert InvalidSwapDeltas();

```

**File:** metric-core/contracts/interfaces/callbacks/IMetricOmmSwapCallback.sol (L9-9)
```text
///      Both deltas may be zero if no settlement is required for that step.
```
