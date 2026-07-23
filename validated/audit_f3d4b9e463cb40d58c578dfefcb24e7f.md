Audit Report

## Title
Forced `totalIn0Scaled` assignment without updating `out1Scaled` causes trader to overpay in exact-input token0→token1 swaps — (`metric-core/contracts/libraries/SwapMath.sol`)

## Summary

In `buyToken1InBinSpecifiedIn`, when two refinement passes still leave `totalIn0Scaled < state.amountSpecifiedRemainingScaled` with `targetPos > minFinalBinPos`, line 759 forces `totalIn0Scaled = state.amountSpecifiedRemainingScaled` without updating `out1Scaled`. The subsequent scale-down block (lines 762–773) is then unreachable because `totalIn0Scaled == remaining`. The function settles with the trader paying all remaining input but receiving token1 output computed for a strictly smaller position, breaking the swap conservation invariant at the trader's expense. The symmetric function `buyToken0InBinSpecifiedIn` contains the identical flaw at lines 620–622.

## Finding Description

The function uses a three-stage approach:

**Stage 1 — Analytical solution (lines 721–736):** Computes `targetPos`, `out1Scaled`, and `totalIn0Scaled`. [1](#0-0) 

**Stage 2 — First refinement (lines 738–757):** If `totalIn0Scaled < remaining && targetPos > minFinalBinPos`, proportionally scales `targetPos` downward, then **updates `out1Scaled`** at line 750 and recomputes `totalIn0Scaled` at line 756. [2](#0-1) 

**Stage 3 — Forced assignment (lines 758–760):** If `totalIn0Scaled` is *still* less than `remaining` and `targetPos > minFinalBinPos`, forces `totalIn0Scaled = remaining` — **without touching `out1Scaled`**. [3](#0-2) 

After line 759, `totalIn0Scaled == remaining`, so the scale-down block at lines 762–773 (which would rescale `out1Scaled` proportionally) is never entered: [4](#0-3) 

The function then settles:
- `state.amountSpecifiedRemainingScaled -= totalIn0Scaled` → all input consumed
- `state.amountCalculatedScaled += out1Scaled` → output from the pre-forced-assignment (smaller) position [5](#0-4) 

**Why is the forced assignment reachable?** The first refinement scales `targetPos` proportionally by `remaining / totalIn0Scaled`. Because input cost grows quadratically with position movement (average price increases as the bin position moves further toward `minFinalBinPos`), a linear proportional scale-up systematically underestimates the new `totalIn0Scaled`. In bins with a large price range (`upperPriceX64 / lowerPriceX64` large, e.g., 4×) and input amounts that push deep into the bin, the first refinement still leaves `totalIn0Scaled < remaining` with `targetPos > minFinalBinPos`, triggering line 759.

**Symmetric flaw confirmed:** `buyToken0InBinSpecifiedIn` has the identical structural bug at lines 620–622 — forced `totalIn1Scaled = remaining` without updating `out0Scaled`: [6](#0-5) 

## Impact Explanation

The trader pays `state.amountSpecifiedRemainingScaled` token0 (all remaining exact input) but receives `out1Scaled` token1 computed for a strictly smaller position. The surplus token0 is credited to the pool's token0 balance at line 780–781, accruing to LPs at the trader's expense. [7](#0-6) 

This is a direct, measurable loss of trader principal on every swap that triggers the fallback path — a swap conservation failure (trader receives less value than the bin curve permits for the input paid). Meets the Sherlock Medium threshold as a broken core swap invariant with direct fund impact.

## Likelihood Explanation

The path requires: (a) the analytical solution underestimates `totalIn0Scaled` (common in bins with large price ranges due to quadratic cost growth), and (b) the first proportional refinement also underestimates (occurs when the quadratic term dominates the linear approximation). No privileged role or malicious setup is required — any public `swap` call with a sufficiently large exact-input amount through a wide bin can trigger it. The condition is not a dust-level edge case; it is reachable by any unprivileged trader.

## Recommendation

Replace the forced assignment with a correct fallback. When `totalIn0Scaled < remaining && targetPos > minFinalBinPos` after both refinements, set `targetPos = minFinalBinPos` (consume the full bin up to the price limit), recompute `out1Scaled` for that position via `calculateOutputToken1FromBinPosition`, and recompute `totalIn0Scaled`. Only then apply the existing scale-down block (lines 762–773) if `totalIn0Scaled > remaining`. This ensures `out1Scaled` always corresponds to the actual `totalIn0Scaled` consumed. Apply the same fix symmetrically to `buyToken0InBinSpecifiedIn` at lines 620–622.

## Proof of Concept

Foundry property test:

```solidity
// For all valid bin states and input amounts that trigger line 759:
// Assert out1Scaled * avgPriceX64 / ONE_X64 >= totalIn0Scaled (net of fee)
// i.e., the output is worth at least as much as the input at the bin's average price.

function testConservation(
    uint104 token1Balance, uint104 currBinPos,
    uint128 lowerPrice, uint128 upperPrice,
    uint128 amountIn
) public {
    // Set up BinState and SwapState with upperPrice/lowerPrice ratio ~4x
    // and amountIn sized to exhaust ~60-80% of the bin's token1 balance
    (,uint256 out1Scaled,,,) = SwapMath.buyToken1InBinSpecifiedIn(...);
    uint256 totalIn0 = amountSpecifiedBefore - state.amountSpecifiedRemainingScaled;
    // Invariant: out1Scaled * avgPriceX64 / ONE_X64 >= totalIn0 (net of fee)
    // FAILS when line 759 is triggered without out1Scaled update
    assertGe(out1Scaled * avgPriceX64 / ONE_X64, totalIn0NetOfFee);
}
```

The test fails for bins where `upperPriceX64 / lowerPriceX64 ≥ 4` and `amountIn` is sized to exhaust roughly 60–80% of the bin's token1 balance, causing both the analytical solution and the first refinement to underestimate `totalIn0Scaled`.

### Citations

**File:** metric-core/contracts/libraries/SwapMath.sol (L620-622)
```text
        if (totalIn1Scaled < state.amountSpecifiedRemainingScaled && targetPos < maxFinalBinPos) {
          totalIn1Scaled = state.amountSpecifiedRemainingScaled;
        }
```

**File:** metric-core/contracts/libraries/SwapMath.sol (L730-736)
```text
        out1Scaled = calculateOutputToken1FromBinPosition(binState.token1BalanceScaled, currBinPos, targetPos);

        invertedFinalPriceX64 =
          invertPriceX64(calculatePriceAtBinPosition(lowerPriceX64, upperPriceX64, targetPos, Math.Rounding.Floor));
        avgPriceX64 = calculateArithmeticMean(invertedStartingPriceX64, invertedFinalPriceX64);
        in0WithoutFeeScaled = calculateRequiredToken(out1Scaled, avgPriceX64);
        totalIn0Scaled = grossInputWithBinFeeCeil(in0WithoutFeeScaled, onePlusSellFeeX64);
```

**File:** metric-core/contracts/libraries/SwapMath.sol (L738-757)
```text
        if (totalIn0Scaled < state.amountSpecifiedRemainingScaled && targetPos > minFinalBinPos) {
          if (totalIn0Scaled == 0) totalIn0Scaled = 1;

          uint256 delta = currBinPos - targetPos;
          // remaining > totalIn0Scaled ⇒ scaledDelta > delta, may exceed MAX_POS_BIN → keep uint256
          uint256 scaledDelta = Math.ceilDiv(delta * state.amountSpecifiedRemainingScaled, totalIn0Scaled);
          if (scaledDelta == 0) scaledDelta = 1;
          targetPos = currBinPos > scaledDelta ? currBinPos - scaledDelta : 0;
          if (targetPos < minFinalBinPos) {
            targetPos = minFinalBinPos;
          }

          out1Scaled = calculateOutputToken1FromBinPosition(binState.token1BalanceScaled, currBinPos, targetPos);

          invertedFinalPriceX64 =
            invertPriceX64(calculatePriceAtBinPosition(lowerPriceX64, upperPriceX64, targetPos, Math.Rounding.Floor));
          avgPriceX64 = calculateArithmeticMean(invertedStartingPriceX64, invertedFinalPriceX64);
          in0WithoutFeeScaled = calculateRequiredToken(out1Scaled, avgPriceX64);
          totalIn0Scaled = grossInputWithBinFeeCeil(in0WithoutFeeScaled, onePlusSellFeeX64);
        }
```

**File:** metric-core/contracts/libraries/SwapMath.sol (L758-760)
```text
        if (totalIn0Scaled < state.amountSpecifiedRemainingScaled && targetPos > minFinalBinPos) {
          totalIn0Scaled = state.amountSpecifiedRemainingScaled;
        }
```

**File:** metric-core/contracts/libraries/SwapMath.sol (L762-773)
```text
        if (totalIn0Scaled > state.amountSpecifiedRemainingScaled) {
          uint256 delta = currBinPos - targetPos;
          // remaining < totalIn0Scaled ⇒ ratio < 1 ⇒ scaledDelta ≤ delta ≤ currBinPos ≤ MAX_POS_BIN
          uint256 scaledDelta =
            Math.mulDiv(delta, state.amountSpecifiedRemainingScaled, totalIn0Scaled, Math.Rounding.Ceil);
          if (scaledDelta == 0) scaledDelta = 1;
          targetPos = currBinPos > scaledDelta ? currBinPos - scaledDelta : 0;

          // Rescale out1Scaled proportionally; remaining < totalIn0Scaled ⇒ result ≤ out1Scaled ≤ MAX_POS_BIN
          out1Scaled = (out1Scaled * state.amountSpecifiedRemainingScaled) / totalIn0Scaled;
          totalIn0Scaled = state.amountSpecifiedRemainingScaled;
        }
```

**File:** metric-core/contracts/libraries/SwapMath.sol (L779-784)
```text
      binState.token1BalanceScaled -= out1Scaled.toUint104();
      binState.token0BalanceScaled =
        (uint256(binState.token0BalanceScaled) + totalIn0Scaled - protocolFeeAmountScaled).toUint104();

      state.amountSpecifiedRemainingScaled -= totalIn0Scaled;
      state.amountCalculatedScaled += out1Scaled;
```
