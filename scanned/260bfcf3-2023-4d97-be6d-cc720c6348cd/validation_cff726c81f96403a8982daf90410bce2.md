Now I have enough context to fully trace the vulnerability. Let me verify the exact arithmetic path.

The vulnerability is **real and confirmed**. The arithmetic trace proves it conclusively.

---

### Title
Exact-input token1→token0 swap silently consumes entire trader input and returns zero token0 when bin `token0BalanceScaled` is dust-small — (`metric-core/contracts/libraries/SwapMath.sol`)

---

### Summary

When a bin's `token0BalanceScaled` is small enough that `token0BalanceScaled × amountSpecifiedRemainingScaled < MAX_POS_BIN`, the `deltaPos=1` minimum-progress guarantee in `computeAnalyticalTargetPosForBuyToken0` triggers a refinement path in `buyToken0InBinSpecifiedIn` that sets `totalIn1Scaled = amountSpecifiedRemainingScaled` while leaving `out0Scaled = 0`. The swap loop then deducts the trader's entire input from `state.amountSpecifiedRemainingScaled` and credits zero to `state.amountCalculatedScaled`, so the trader pays in full and receives nothing.

---

### Finding Description

**Step-by-step arithmetic trace** (currBinPos = 0, token0BalanceScaled = T, amountSpecifiedRemainingScaled = I, maxFinalBinPos = MAX_POS_BIN ≈ 2¹⁰⁴):

**1. `computeAnalyticalTargetPosForBuyToken0` returns `targetPos = 1`.**

The closed-form quadratic rounds `deltaPos` to 0 (because T is tiny relative to MAX_POS_BIN), then the minimum-progress guard fires:

```
if (deltaPos == 0 && inputAmount > 0) deltaPos = 1;
``` [1](#0-0) 

**2. `out0Scaled` rounds to zero.**

```
outToken0 = (availableToken0 * (finalBinPos - currBinPos)) / (MAX_POS_BIN - currBinPos);
// = (T * 1) / MAX_POS_BIN = 0  (integer division, T < MAX_POS_BIN always)
``` [2](#0-1) 

**3. `totalIn1Scaled` also rounds to zero** (ceilDiv of 0 is 0).

**4. First refinement block (line 598) fires** because `totalIn1Scaled (0) < amountSpecifiedRemainingScaled (I)` and `targetPos (1) < maxFinalBinPos`:

```solidity
if (totalIn1Scaled == 0) totalIn1Scaled = 1;
uint256 scaledDelta = Math.ceilDiv(delta * state.amountSpecifiedRemainingScaled, totalIn1Scaled);
// = ceilDiv(1 * I, 1) = I
uint256 scaledTarget = currBinPos + scaledDelta; // = I
``` [3](#0-2) 

`targetPos` is now set to `I` (assuming `I < MAX_POS_BIN`).

**5. `out0Scaled` is recomputed with the new `targetPos = I`:**

```
out0Scaled = (T * I) / MAX_POS_BIN
```

This is still **0** whenever `T × I < MAX_POS_BIN`. For a 1e18-unit input, this holds for any `T < 2¹⁰⁴ / 1e18 ≈ 1.76 × 10¹³`. [4](#0-3) 

**6. Second guard (line 620) fires** because `totalIn1Scaled (0) < I` and `targetPos (I) < MAX_POS_BIN`:

```solidity
if (totalIn1Scaled < state.amountSpecifiedRemainingScaled && targetPos < maxFinalBinPos) {
    totalIn1Scaled = state.amountSpecifiedRemainingScaled; // = I
}
``` [5](#0-4) 

**7. Line 624 does NOT fire** (`totalIn1Scaled == amountSpecifiedRemainingScaled`, not `>`).

**8. Final accounting:**

```solidity
state.amountSpecifiedRemainingScaled -= totalIn1Scaled; // -= I → 0
state.amountCalculatedScaled += out0Scaled;             // += 0
``` [6](#0-5) 

The bin absorbs `I - protocolFee` token1 (LP gains), emits 0 token0 (trader loses everything).

**9. The swap loop terminates** because `amountSpecifiedRemainingScaled = 0`, so no further bins are visited. The pool returns `(amountInScaled, 0, protocolFeeAmountScaled)` — full input consumed, zero output. [7](#0-6) 

**The `nonEmptyBin` guard does not protect against this.** It only skips bins where `token0BalanceScaled == 0`. A bin with `token0BalanceScaled = 1` (or any value satisfying `T × I < MAX_POS_BIN`) passes the guard and enters `buyToken0InBinSpecifiedIn`. [8](#0-7) 

**The minimum-input guard at line 550 does not protect against this either.** It only rejects inputs where `amountSpecifiedRemainingScaled × 2⁶⁴ < startingPriceX64` — a price-floor check, not a balance-floor check. [9](#0-8) 

---

### Impact Explanation

**Direct loss of user principal.** The trader's entire token1 input is consumed by the pool; the LP in the affected bin receives token1 for free with no token0 leaving the bin. The corrupted value is `state.amountCalculatedScaled` (remains 0 while `amountSpecifiedRemainingScaled` is fully decremented). This satisfies the contest's "Critical/High direct loss of user principal" gate.

---

### Likelihood Explanation

The condition `token0BalanceScaled × amountSpecifiedRemainingScaled < MAX_POS_BIN` is reachable in normal operation:

- After a large swap drains a bin to a dust balance (e.g., 1 to ~10¹³ scaled units), the next trader hitting that bin with a standard-sized input (≥ 1e18 scaled) triggers the bug.
- An attacker can deliberately drain a bin to dust in one transaction, then front-run a victim's swap in the next.
- No privileged access, malicious pool setup, or non-standard tokens are required — only a public `swap` call on a pool with a partially-drained bin.

---

### Recommendation

In `buyToken0InBinSpecifiedIn`, after computing `out0Scaled` (both initially and after each refinement step), add an early-exit guard:

```solidity
if (out0Scaled == 0) {
    // Cannot extract any token0 from this bin at this position; skip.
    return (currBinPos, 0, 0, 0, 0);
}
```

This mirrors the existing guard in `buyToken0InBinSpecifiedOut` (which already returns early when output rounds to zero) and prevents the refinement loop from incorrectly charging input against a zero-output move. [10](#0-9) 

---

### Proof of Concept

```solidity
// token0BalanceScaled = 1, currBinPos = 0, amountSpecifiedRemainingScaled = 1e18
// lowerPriceX64 = 1e18, upperPriceX64 = 2e18, priceLimitX64 = type(uint128).max

BinState memory binState = BinState({
    token0BalanceScaled: 1,   // dust balance
    token1BalanceScaled: 0,
    lengthE6: 1,
    addFeeBuyE6: 0,
    addFeeSellE6: 0
});

SwapMath.SwapState memory state = SwapMath.SwapState({
    amountSpecifiedRemainingScaled: 1e18,
    amountCalculatedScaled: 0,
    protocolFeeAmountScaled: 0,
    feeExclusiveInputScaled: 0
});

(uint256 finalBinPos, uint256 out0Scaled,,,) = SwapMath.buyToken0InBinSpecifiedIn(
    binState, 0, state, 0, 1e18, 2e18, type(uint128).max, 0
);

// Assertions that demonstrate the bug:
assert(out0Scaled == 0);                              // trader receives nothing
assert(state.amountSpecifiedRemainingScaled == 0);    // entire input consumed
assert(state.amountCalculatedScaled == 0);            // zero credited to trader
// 1e18 token1 paid, 0 token0 received — full principal loss
```

### Citations

**File:** metric-core/contracts/libraries/SwapMath.sol (L208-208)
```text
      outToken0 = (availableToken0 * (finalBinPos - currBinPos)) / (MAX_POS_BIN - currBinPos);
```

**File:** metric-core/contracts/libraries/SwapMath.sol (L284-284)
```text
    if (deltaPos == 0 && inputAmount > 0) deltaPos = 1;
```

**File:** metric-core/contracts/libraries/SwapMath.sol (L550-552)
```text
      if ((state.amountSpecifiedRemainingScaled << 64) < startingPriceX64) {
        return (currBinPos, 0, 0, 0, 0);
      }
```

**File:** metric-core/contracts/libraries/SwapMath.sol (L591-596)
```text
        out0Scaled = calculateOutputToken0FromBinPosition(binState.token0BalanceScaled, currBinPos, targetPos);

        finalPriceX64 = calculatePriceAtBinPosition(lowerPriceX64, upperPriceX64, targetPos, Math.Rounding.Ceil);
        avgPriceX64 = calculateArithmeticMean(startingPriceX64, finalPriceX64);
        in1WithoutFeeScaled = calculateRequiredToken(out0Scaled, avgPriceX64);
        totalIn1Scaled = grossInputWithBinFeeCeil(in1WithoutFeeScaled, onePlusBuyFeeX64);
```

**File:** metric-core/contracts/libraries/SwapMath.sol (L598-610)
```text
        if (totalIn1Scaled < state.amountSpecifiedRemainingScaled && targetPos < maxFinalBinPos) {
          if (totalIn1Scaled == 0) totalIn1Scaled = 1;
          uint256 delta = targetPos - currBinPos;
          // remaining > totalIn1Scaled ⇒ scaledDelta > delta, may exceed MAX_POS_BIN → keep uint256
          uint256 scaledDelta = Math.ceilDiv(delta * state.amountSpecifiedRemainingScaled, totalIn1Scaled);
          if (scaledDelta == 0) scaledDelta = 1;
          uint256 scaledTarget = currBinPos + scaledDelta;
          if (scaledTarget > maxFinalBinPos) {
            targetPos = maxFinalBinPos;
          } else {
            // Safe: scaledTarget ≤ maxFinalBinPos ≤ MAX_POS_BIN
            targetPos = scaledTarget;
          }
```

**File:** metric-core/contracts/libraries/SwapMath.sol (L612-617)
```text
          out0Scaled = calculateOutputToken0FromBinPosition(binState.token0BalanceScaled, currBinPos, targetPos);

          finalPriceX64 = calculatePriceAtBinPosition(lowerPriceX64, upperPriceX64, targetPos, Math.Rounding.Ceil);
          avgPriceX64 = calculateArithmeticMean(startingPriceX64, finalPriceX64);
          in1WithoutFeeScaled = calculateRequiredToken(out0Scaled, avgPriceX64);
          totalIn1Scaled = grossInputWithBinFeeCeil(in1WithoutFeeScaled, onePlusBuyFeeX64);
```

**File:** metric-core/contracts/libraries/SwapMath.sol (L620-622)
```text
        if (totalIn1Scaled < state.amountSpecifiedRemainingScaled && targetPos < maxFinalBinPos) {
          totalIn1Scaled = state.amountSpecifiedRemainingScaled;
        }
```

**File:** metric-core/contracts/libraries/SwapMath.sol (L643-644)
```text
      state.amountSpecifiedRemainingScaled -= totalIn1Scaled;
      state.amountCalculatedScaled += out0Scaled;
```

**File:** metric-core/contracts/MetricOmmPool.sol (L977-986)
```text
        bool nonEmptyBin = true;
        if (binState.token0BalanceScaled == 0 || curPosInBinCache >= type(uint104).max) {
          if (params.priceLimitX64 != 0 && params.priceLimitX64 <= upperPriceX64) {
            break;
          }
          if (totalAvailableToken0Scaled == 0) {
            break;
          }
          nonEmptyBin = false;
        }
```

**File:** metric-core/contracts/MetricOmmPool.sol (L1033-1037)
```text
      return (
        amountInScaled - state.amountSpecifiedRemainingScaled,
        state.amountCalculatedScaled,
        state.protocolFeeAmountScaled
      );
```
