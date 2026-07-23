### Title
Exact-Output Swap Silently Delivers Less Than Requested Amount Without Reverting — (`metric-core/contracts/MetricOmmPool.sol`, `metric-core/contracts/libraries/SwapMath.sol`)

### Summary

The Metric OMM pool's exact-output swap path (`amountSpecified < 0`) silently caps the output to available liquidity and proceeds without reverting, breaking the exact-output invariant at the pool level. Any direct integrator that does not validate the returned deltas will receive fewer tokens than requested with no on-chain signal of failure.

### Finding Description

When `swap()` is called with a negative `amountSpecified` (exact-output mode), the pool internally calls `_swapToken0ForToken1SpecifiedOutput` or `_swapToken1ForToken0SpecifiedOutput`. Both functions begin with an unconditional silent cap:

```solidity
// _swapToken0ForToken1SpecifiedOutput (zeroForOne exact-out)
uint256 totalAvailableToken1Scaled = binTotals.scaledToken1;
if (amountOutScaled > totalAvailableToken1Scaled) {
    amountOutScaled = totalAvailableToken1Scaled;   // ← silent reduction, no revert
}
``` [1](#0-0) 

The symmetric cap exists for the `!zeroForOne` direction: [2](#0-1) 

After the cap, the swap loop executes against the reduced target. The actual output delivered to `recipient` is `amountOutScaled - state.amountSpecifiedRemainingScaled`, which can be strictly less than the original `|amountSpecified|`. The pool then transfers only the reduced amount:

```solidity
if (amount1Delta < 0) {
    transferToken1(recipient, uint256(-amount1Delta));   // reduced amount
}
``` [3](#0-2) 

The only post-callback check (`IncorrectDelta`) verifies that the **caller paid enough input token**, not that the **output equalled the requested amount**:

```solidity
if (amount0Delta > 0 && balance0Before + uint256(amount0Delta) > balance0()) {
    revert IncorrectDelta();
}
``` [4](#0-3) 

There is no corresponding guard that reverts when `actual output < requested output`. The pool returns the actual (reduced) `amount0Delta`/`amount1Delta` to the caller, but does not enforce the exact-output invariant itself.

The periphery router does enforce this — `exactOutputSingle` and `exactOutput` both revert on shortfall:

```solidity
if (amountOut != expectedAmountOut) revert InvalidOutputAmount(amountOut, params.amountOut);
``` [5](#0-4) 

```solidity
if (amountOut != amountToPay) revert InvalidOutputAmountAtHop(tradesLeft, amountOut, amountToPay);
``` [6](#0-5) 

But the pool is a public, permissionless contract. Any protocol that integrates directly with `MetricOmmPool.swap()` — bypassing the router — and does not inspect the returned deltas will silently receive fewer tokens than requested.

### Impact Explanation

A direct integrator (e.g., a lending protocol, aggregator, or settlement contract) that calls `pool.swap(recipient, zeroForOne, -N, ...)` expecting exactly `N` output tokens will:

1. Receive fewer than `N` tokens transferred to `recipient`.
2. Pay only for the reduced amount (no overcharge), but proceed with an incorrect assumption about how many tokens were received.
3. Suffer downstream failures: underpaid debt repayments, incomplete arbitrage legs, incorrect accounting, or loss of funds if the contract uses the assumed `N` tokens for further operations.

This is a direct analog to the EIP-4626 `withdraw` non-compliance: a function with exact-output semantics silently delivers less than requested without reverting.

### Likelihood Explanation

The pool is a core, publicly callable contract. The `swap` interface is the primary integration surface for any protocol building on Metric OMM. The condition that triggers the bug — requesting more output than is currently available across all bins — is a normal operational state (e.g., low liquidity, large order, or concurrent withdrawals). Any integrator that does not replicate the router's output-equality check is exposed.

### Recommendation

The pool should enforce the exact-output invariant directly. After `_executeSwap` returns, add a check that reverts when the actual output is less than the requested output in exact-output mode:

```solidity
// In swap(), after _executeSwap:
if (amountSpecified < 0) {
    // exact-output: actual output must equal requested output
    int256 requestedOut = -int256(int128(amountSpecified));
    int256 actualOut = zeroForOne ? -amount1Delta : -amount0Delta;
    if (actualOut < requestedOut) revert InsufficientOutput();
}
```

Alternatively, the capping logic inside `_swapToken0ForToken1SpecifiedOutput` and `_swapToken1ForToken0SpecifiedOutput` should revert instead of silently reducing `amountOutScaled` when the requested output exceeds available liquidity.

### Proof of Concept

1. Pool has `binTotals.scaledToken1 = 50e6 * TOKEN_1_SCALE_MULTIPLIER` (50 USDC worth of token1 across all bins).
2. Integrator contract calls `pool.swap(recipient, true, -100e6, 0, callbackData, "")` expecting exactly 100 USDC.
3. Inside `_swapToken0ForToken1SpecifiedOutput`: `amountOutScaled` is capped from `100e6 * scale` to `50e6 * scale`.
4. Swap executes; pool transfers 50 USDC to `recipient`.
5. Callback fires; integrator pays token0 equivalent of 50 USDC (correctly priced for the reduced output).
6. `IncorrectDelta` check passes (input was sufficient for the reduced output).
7. `swap()` returns `amount1Delta = -50e6` — no revert.
8. Integrator contract assumed it received 100 USDC; it received 50 USDC. Any downstream logic (debt repayment, order fulfillment) that assumed 100 USDC is now broken or causes loss of funds. [7](#0-6) [8](#0-7)

### Citations

**File:** metric-core/contracts/MetricOmmPool.sol (L247-278)
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

**File:** metric-core/contracts/MetricOmmPool.sol (L871-876)
```text
      {
        uint256 totalAvailableToken0Scaled = binTotals.scaledToken0;
        if (amountOutScaled > totalAvailableToken0Scaled) {
          amountOutScaled = totalAvailableToken0Scaled;
        }
      }
```

**File:** metric-core/contracts/MetricOmmPool.sol (L1043-1053)
```text
  function _swapToken0ForToken1SpecifiedOutput(uint256 amountOutScaled, SwapMath.InternalSwapParams memory params)
    internal
    returns (uint256, uint256, uint256, uint256)
  {
    unchecked {
      {
        uint256 totalAvailableToken1Scaled = binTotals.scaledToken1;
        if (amountOutScaled > totalAvailableToken1Scaled) {
          amountOutScaled = totalAvailableToken1Scaled;
        }
      }
```

**File:** metric-periphery/contracts/MetricOmmSimpleRouter.sol (L139-139)
```text
    if (amountOut != expectedAmountOut) revert InvalidOutputAmount(amountOut, params.amountOut);
```

**File:** metric-periphery/contracts/MetricOmmSimpleRouter.sol (L232-232)
```text
    if (amountOut != amountToPay) revert InvalidOutputAmountAtHop(tradesLeft, amountOut, amountToPay);
```
