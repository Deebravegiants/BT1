The code trace is complete. Here is the verdict:

---

### Title
Exact-Output Swap Silently Delivers Partial Fill Without Reverting — (`metric-core/contracts/MetricOmmPool.sol`)

### Summary
`_swapToken0ForToken1SpecifiedOutput` (and its mirror `_swapToken1ForToken0SpecifiedOutput`) silently caps `amountOutScaled` to `totalAvailableToken1Scaled` when the pool holds less token1 than requested, then returns the capped actual output. The `swap` function transfers only the capped amount to the recipient and passes the reduced `amount1Delta` to the callback. The `IncorrectDelta` guard checks only that the pool received the correct input token; it never verifies that the output equals the originally requested amount. The transaction succeeds without reverting.

### Finding Description

**Step 1 — Entry:** `swap(recipient, zeroForOne=true, amountSpecified=-N, ...)` with `N > pool's available token1`.

**Step 2 — Scale:** In `_executeSwap` line 708:
```
amountOutScaled = TOKEN_1_SCALE_MULTIPLIER * uint256(-amountSpecified)
               = TOKEN_1_SCALE_MULTIPLIER * N
``` [1](#0-0) 

**Step 3 — Silent cap:** In `_swapToken0ForToken1SpecifiedOutput` lines 1049–1052:
```solidity
uint256 totalAvailableToken1Scaled = binTotals.scaledToken1;
if (amountOutScaled > totalAvailableToken1Scaled) {
    amountOutScaled = totalAvailableToken1Scaled;   // silently reduced
}
``` [2](#0-1) 

The function then runs the bin loop against the capped target and returns `amountOutScaled - state.amountSpecifiedRemainingScaled` as the actual output — which is ≤ the capped value, and strictly less than the originally requested `N * TOKEN_1_SCALE_MULTIPLIER`. [3](#0-2) 

**Step 4 — Transfer:** Back in `swap`, the pool transfers only `uint256(-amount1Delta)` (the capped amount) to the recipient:
```solidity
transferToken1(recipient, uint256(-amount1Delta));
``` [4](#0-3) 

**Step 5 — Callback and guard:** The callback receives `amount1Delta = -(capped amount)` and pays `amount0Delta` (computed from the capped output). The `IncorrectDelta` check only verifies the pool received the correct token0 input:
```solidity
if (amount0Delta > 0 && balance0Before + uint256(amount0Delta) > balance0()) {
    revert IncorrectDelta();
}
```
There is **no check** that `amount1Delta == -(N * TOKEN_1_SCALE_MULTIPLIER)`. The transaction succeeds. [5](#0-4) 

### Impact Explanation
The exact-output invariant — "deliver exactly N tokens or revert" — is broken at the pool level. Any router or integrator that calls `swap` with `amountSpecified < 0` and relies on receiving exactly the requested output will silently receive fewer tokens. In multi-hop or aggregator contexts where the output of this swap is the input of a downstream step, the shortfall propagates: the downstream step receives less than expected, causing it to either revert (wasting gas and failing the user's trade) or, if it does not validate, to deliver fewer tokens to the end user than promised. The pool itself does not lose funds, but the trader/recipient is shortchanged above Sherlock Medium thresholds whenever the pool is under-liquid relative to the request.

### Likelihood Explanation
Any pool that has been partially drained by prior swaps or has low liquidity relative to a large exact-output request is vulnerable. No privileged access is required — any public caller can trigger this via the `swap` entrypoint. The condition (`requested > available`) is a normal operational state for any active pool.

### Recommendation
Add a revert after the swap loop in both `_swapToken0ForToken1SpecifiedOutput` and `_swapToken1ForToken0SpecifiedOutput` if `state.amountSpecifiedRemainingScaled > 0` (i.e., the full requested output was not filled):

```solidity
// After the while loop, before _finalizeSwap:
require(state.amountSpecifiedRemainingScaled == 0, InsufficientLiquidityForExactOutput());
```

Alternatively, if partial fills are intentional, the `swap` interface must document this and routers must be updated to check `amount1Delta` against the originally requested amount and revert if they differ.

### Proof of Concept
```solidity
// Foundry integration test sketch
function test_exactOutput_partialFill_noRevert() public {
    // Pool holds 100 token1 (scaled)
    // Trader requests exact output of 200 token1
    int128 amountSpecified = -200; // exact-out

    uint256 recipientBefore = token1.balanceOf(recipient);
    (int256 amt0, int256 amt1) = pool.swap(
        recipient, true, amountSpecified, 0, callbackData, ""
    );
    uint256 recipientAfter = token1.balanceOf(recipient);

    // Pool did NOT revert
    // Recipient received < 200 token1
    assertLt(recipientAfter - recipientBefore, 200, "partial fill: received less than requested");
    // amt1 is less negative than -200 * TOKEN_1_SCALE_MULTIPLIER
    assertGt(amt1, int256(-200) * int256(TOKEN_1_SCALE_MULTIPLIER), "amount1Delta not equal to requested");
}
```

### Citations

**File:** metric-core/contracts/MetricOmmPool.sol (L251-255)
```text
      if (amount1Delta < 0) {
        // casting to uint256 is safe because amount1Delta is negative and the ammount of tokens in pool is capped by uint128.max
        // forge-lint: disable-next-line(unsafe-typecast)
        transferToken1(recipient, uint256(-amount1Delta));
      }
```

**File:** metric-core/contracts/MetricOmmPool.sol (L257-263)
```text
      uint256 balance0Before = balance0();
      IMetricOmmSwapCallback(msg.sender).metricOmmSwapCallback(amount0Delta, amount1Delta, callbackData);
      // casting to uint256 is safe because amount0Delta is positive and the ammount of tokens in pool is capped by uint128.max
      // forge-lint: disable-next-line(unsafe-typecast)
      if (amount0Delta > 0 && balance0Before + uint256(amount0Delta) > balance0()) {
        revert IncorrectDelta();
      }
```

**File:** metric-core/contracts/MetricOmmPool.sol (L706-715)
```text
        if (zeroForOne) {
          // forge-lint: disable-next-line(unsafe-typecast)
          uint256 amountOutScaled = TOKEN_1_SCALE_MULTIPLIER * uint256(-amountSpecified);
          uint256 amountInScaled;
          (amountInScaled, amountOutScaled, protocolFeeScaled, feeExclusiveInputScaled) =
            _swapToken0ForToken1SpecifiedOutput(amountOutScaled, params);
          // forge-lint: disable-next-line(unsafe-typecast)
          amount0DeltaScaled = int256(amountInScaled);
          // forge-lint: disable-next-line(unsafe-typecast)
          amount1DeltaScaled = -int256(amountOutScaled);
```

**File:** metric-core/contracts/MetricOmmPool.sol (L1049-1052)
```text
        uint256 totalAvailableToken1Scaled = binTotals.scaledToken1;
        if (amountOutScaled > totalAvailableToken1Scaled) {
          amountOutScaled = totalAvailableToken1Scaled;
        }
```

**File:** metric-core/contracts/MetricOmmPool.sol (L1121-1126)
```text
      return (
        state.amountCalculatedScaled,
        amountOutScaled - state.amountSpecifiedRemainingScaled,
        state.protocolFeeAmountScaled,
        state.feeExclusiveInputScaled
      );
```
