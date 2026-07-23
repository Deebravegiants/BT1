Audit Report

## Title
Unconditional `metricOmmSwapCallback` invocation with zero deltas causes `MetricOmmSimpleRouter` to always revert on no-op swaps - (`metric-core/contracts/MetricOmmPool.sol`)

## Summary

`MetricOmmPool.swap()` fires `metricOmmSwapCallback` on `msg.sender` unconditionally after `_executeSwap`, including when it returns `(0, 0, 0)`. `MetricOmmSimpleRouter.metricOmmSwapCallback()` reverts with `InvalidSwapDeltas` whenever `amount0Delta <= 0 && amount1Delta <= 0`, which is satisfied by `(0, 0)`. Any swap through the router that legitimately produces zero deltas — a documented, reachable state — permanently reverts.

## Finding Description

**Unconditional callback in `MetricOmmPool.swap()`:**

After `_executeSwap` returns, both branches fire the callback with no guard on whether either delta is non-zero: [1](#0-0) [2](#0-1) 

**`_executeSwap` legitimately returns `(0, 0, 0)`:**

The internal swap helper explicitly returns `(0, 0, 0)` when the price limit is immediately satisfied (4 such return sites exist in `MetricOmmPool.sol`): [3](#0-2) 

**Router guard reverts on zero deltas:** [4](#0-3) 

When the pool calls this with `(0, 0, callbackData)`, the condition `0 <= 0 && 0 <= 0` is `true`, so `InvalidSwapDeltas` is thrown and the entire transaction reverts.

**Contrast with `LiquidityLib.addLiquidity`**, which correctly guards its callback: [5](#0-4) 

The pattern `if (amount0Added > 0 || amount1Added > 0)` exists in the codebase but is absent from the swap path.

**Execution path:**
1. User calls `MetricOmmSimpleRouter.exactInputSingle()` with a `priceLimitX64` that is at or beyond the current oracle price.
2. `normalizePriceLimit` passes the value through unchanged (or maps sentinel to 0/max).
3. Pool calls `_executeSwap` → internal helper returns `(0, 0, 0)`.
4. Pool unconditionally calls `metricOmmSwapCallback(0, 0, "")` on the router.
5. Router guard fires: `revert InvalidSwapDeltas()`.
6. Entire transaction reverts. [6](#0-5) 

## Impact Explanation

Any swap routed through `MetricOmmSimpleRouter` — the primary user-facing router — that results in zero deltas is permanently blocked. This breaks the core swap flow for `exactInputSingle`, `exactOutputSingle`, and multi-hop `exactInput`/`exactOutput` paths where an intermediate hop produces zero deltas. This constitutes broken core pool/router functionality for a documented, valid input range. No user funds are directly drained, but the swap path is rendered unusable for this class of inputs, meeting the "broken core pool functionality" allowed impact.

## Likelihood Explanation

The zero-delta case is reachable by any unprivileged caller via a standard `exactInputSingle` call. It occurs whenever the caller supplies a `priceLimitX64` that is at or beyond the current oracle mid-price (e.g., a conservative slippage guard that the oracle has already moved past), or when the oracle price moves between transaction submission and execution, pushing the limit into the immediately-satisfied range. Both scenarios are normal in live trading conditions.

## Recommendation

**Option A (preferred — fix in pool):** Skip the callback entirely when both deltas are zero, mirroring the `LiquidityLib` pattern:

```solidity
// In MetricOmmPool.swap(), before firing the callback:
if (amount0Delta != 0 || amount1Delta != 0) {
    IMetricOmmSwapCallback(msg.sender).metricOmmSwapCallback(amount0Delta, amount1Delta, callbackData);
}
```

**Option B (fix in router):** Change the router guard to distinguish zero from negative, and return early on zero-delta no-ops:

```solidity
if (amount0Delta < 0 && amount1Delta < 0) revert InvalidSwapDeltas();
if (amount0Delta == 0 && amount1Delta == 0) return;
```

## Proof of Concept

```solidity
// Setup: deploy pool with token0/token1, add liquidity, deploy MetricOmmSimpleRouter.
// For !zeroForOne direction, priceLimitX64=1 is immediately satisfied
// because initialPriceX64 > 1 for any real oracle price.

router.exactInputSingle(
    IMetricOmmSimpleRouter.ExactInputSingleParams({
        pool: address(pool),
        recipient: address(this),
        zeroForOne: false,
        amountIn: 1000,
        amountOutMinimum: 0,
        priceLimitX64: 1,           // immediately satisfied: 1 < initialPriceX64
        tokenIn: address(token1),
        deadline: block.timestamp + 1,
        extensionData: ""
    })
);
// Expected: succeeds with zero output (no-op swap)
// Actual:   reverts with InvalidSwapDeltas() because:
//   1. _executeSwap returns (0, 0, 0) at MetricOmmPool.sol:1148-1150
//   2. Pool calls metricOmmSwapCallback(0, 0, "") unconditionally
//   3. Router guard at MetricOmmSimpleRouter.sol:47 fires: 0<=0 && 0<=0 == true
```

### Citations

**File:** metric-core/contracts/MetricOmmPool.sol (L247-258)
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

**File:** metric-periphery/contracts/MetricOmmSimpleRouter.sol (L46-47)
```text
  function metricOmmSwapCallback(int256 amount0Delta, int256 amount1Delta, bytes calldata data) external override {
    if (amount0Delta <= 0 && amount1Delta <= 0) revert InvalidSwapDeltas();
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

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L144-148)
```text
      if (amount0Added > 0 || amount1Added > 0) {
        uint256 balance0Before = IERC20(ctx.token0).balanceOf(address(this));
        uint256 balance1Before = IERC20(ctx.token1).balanceOf(address(this));
        IMetricOmmModifyLiquidityCallback(msg.sender)
          .metricOmmModifyLiquidityCallback(amount0Added, amount1Added, callbackData);
```
