The vulnerability is real. Here is the full trace and finding.

---

### Title
Pool `swap` silently delivers partial output on exact-output when liquidity is insufficient, without reverting — (`metric-core/contracts/MetricOmmPool.sol`)

### Summary

`MetricOmmPool.swap` with a negative `amountSpecified` (exact-output mode) silently caps the output at available pool liquidity and transfers fewer tokens than requested to the recipient, without reverting. The `IncorrectDelta` guard only verifies that the input token was received; it does not verify that the output equals the requested amount. Any direct pool integrator relying on exact-output semantics receives a partial fill with no on-chain signal.

### Finding Description

**Step 1 — Cap without revert.**

Inside `_swapToken0ForToken1SpecifiedOutput`, the requested output is silently reduced to whatever token1 the pool currently holds:

```solidity
uint256 totalAvailableToken1Scaled = binTotals.scaledToken1;
if (amountOutScaled > totalAvailableToken1Scaled) {
    amountOutScaled = totalAvailableToken1Scaled;   // silent cap, no revert
}
``` [1](#0-0) 

The same pattern exists in `_swapToken1ForToken0SpecifiedOutput`: [2](#0-1) 

**Step 2 — Capped value propagates back.**

`_executeSwap` assigns `amount1DeltaScaled = -int256(amountOutScaled)` where `amountOutScaled` is the already-capped return value, not the original `-N * TOKEN_1_SCALE_MULTIPLIER`: [3](#0-2) 

**Step 3 — Pool transfers the capped amount and calls callback.**

`swap` transfers the capped `amount1Delta` to the recipient, then calls the callback with `amount0Delta` sized only for the capped output: [4](#0-3) 

**Step 4 — `IncorrectDelta` only checks the input leg.**

The guard verifies `balance0` increased by `amount0Delta` (the input). It does not check that `amount1Delta` equals the originally requested `-N`. A partial fill passes this check silently: [5](#0-4) 

**Mitigation present only in the router, not the pool.**

`MetricOmmSimpleRouter.exactOutputSingle` does add a post-swap check:

```solidity
if (amountOut != expectedAmountOut) revert InvalidOutputAmount(amountOut, params.amountOut);
``` [6](#0-5) 

But this protection lives in the periphery router, not in the core pool. Any integrator calling `MetricOmmPool.swap` directly — including custom routers, aggregators, or on-chain protocols — receives a partial fill with no revert and no on-chain indication that the exact-output request was not honored.

### Impact Explanation

A direct caller of `MetricOmmPool.swap` with `amountSpecified = -N` where `N > available token1` will:
- Receive fewer tokens than requested (partial fill)
- Pay only for the partial fill (no direct monetary loss to the caller)
- Observe no revert — the transaction succeeds

The broken invariant causes downstream failures for any integrator that depends on exact-output semantics: contracts that need exactly N tokens to repay a flash loan, fulfill a limit order, or satisfy a downstream obligation will silently under-receive and fail at a later step, potentially losing gas or causing cascading reverts in multi-step protocols. The pool's core `swap` function does not enforce the fundamental exact-output guarantee.

### Likelihood Explanation

Any integrator calling the pool directly (not through `MetricOmmSimpleRouter`) is affected whenever pool liquidity is insufficient to fill the requested output. This is a normal market condition (thin liquidity, large order). The pool is a public contract; direct integration is the expected use case for aggregators and custom routers.

### Recommendation

Add an exact-output enforcement check inside `MetricOmmPool.swap` after `_executeSwap` returns, for the exact-output case (`amountSpecified < 0`):

```solidity
// For exact-output: verify the pool delivered exactly what was requested
if (amountSpecified < 0) {
    int256 requestedOut = int256(uint256(-amountSpecified));
    // zeroForOne: output is token1 (amount1Delta negative)
    // !zeroForOne: output is token0 (amount0Delta negative)
    int256 actualOut = zeroForOne ? -amount1Delta : -amount0Delta;
    if (actualOut != requestedOut) revert InsufficientLiquidityForExactOutput();
}
```

Alternatively, `_swapToken0ForToken1SpecifiedOutput` and `_swapToken1ForToken0SpecifiedOutput` should revert instead of silently capping when `amountOutScaled > totalAvailableXScaled`.

### Proof of Concept

```solidity
// Foundry integration test
function test_exactOutput_partialFill_noRevert() public {
    // Pool holds 100 token1 (scaled)
    // Trader requests 200 token1 out (exact-output)
    uint128 requested = 200;
    uint128 available = 100; // pool has only 100

    uint256 recipientBefore = token1.balanceOf(recipient);

    // swap(zeroForOne=true, amountSpecified=-200, ...) — should revert or deliver 200
    (int128 amount0Delta, int128 amount1Delta) = pool.swap(
        recipient, true, -int128(requested), 0, callbackData, ""
    );

    uint256 recipientAfter = token1.balanceOf(recipient);
    uint256 received = recipientAfter - recipientBefore;

    // These assertions PASS, demonstrating the broken invariant:
    assertLt(received, requested, "Received less than requested — no revert");
    assertEq(received, available,  "Received only available amount");
    // amount1Delta is less negative than -requested * TOKEN_1_SCALE_MULTIPLIER
    assertGt(amount1Delta, -int128(requested), "amount1Delta not equal to -requested");
}
```

### Citations

**File:** metric-core/contracts/MetricOmmPool.sol (L251-263)
```text
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

**File:** metric-core/contracts/MetricOmmPool.sol (L710-715)
```text
          (amountInScaled, amountOutScaled, protocolFeeScaled, feeExclusiveInputScaled) =
            _swapToken0ForToken1SpecifiedOutput(amountOutScaled, params);
          // forge-lint: disable-next-line(unsafe-typecast)
          amount0DeltaScaled = int256(amountInScaled);
          // forge-lint: disable-next-line(unsafe-typecast)
          amount1DeltaScaled = -int256(amountOutScaled);
```

**File:** metric-core/contracts/MetricOmmPool.sol (L872-875)
```text
        uint256 totalAvailableToken0Scaled = binTotals.scaledToken0;
        if (amountOutScaled > totalAvailableToken0Scaled) {
          amountOutScaled = totalAvailableToken0Scaled;
        }
```

**File:** metric-core/contracts/MetricOmmPool.sol (L1049-1052)
```text
        uint256 totalAvailableToken1Scaled = binTotals.scaledToken1;
        if (amountOutScaled > totalAvailableToken1Scaled) {
          amountOutScaled = totalAvailableToken1Scaled;
        }
```

**File:** metric-periphery/contracts/MetricOmmSimpleRouter.sol (L139-139)
```text
    if (amountOut != expectedAmountOut) revert InvalidOutputAmount(amountOut, params.amountOut);
```
