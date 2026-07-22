### Title
Arithmetic Mean Mid Price in `OracleValueStopLossExtension` Diverges from Pool's Geometric Mean, Miscalibrating LP Value Protection — (`metric-periphery/contracts/extensions/OracleValueStopLossExtension.sol`)

### Summary

`OracleValueStopLossExtension._afterSwapOracleStopLoss()` computes the oracle mid price as the **arithmetic mean** `(bid + ask) / 2`, while the pool's canonical swap math (`SwapMath.midAndSpreadFeeX64FromBidAsk`) uses the **geometric mean** `sqrt(bid * ask)`. This is the direct Metric OMM analog of the external report's "wrong denomination" root cause: a price quantity used for a protection/accounting invariant is computed in a different unit than the quantity the pool itself uses, causing systematic miscalibration of LP value watermarks.

### Finding Description

In `_afterSwapOracleStopLoss()`:

```solidity
uint256 midPriceX64 = (uint256(bidPriceX64) + uint256(askPriceX64)) / 2;
``` [1](#0-0) 

But the pool's swap math computes the canonical mid price as:

```solidity
midPriceX64 = Math.sqrt(bidPriceX64 * askPriceX64);
``` [2](#0-1) 

By the AM-GM inequality, `(bid + ask)/2 ≥ sqrt(bid * ask)` with equality only when `bid == ask`. So the extension always uses a mid price that is **strictly higher** than the pool's canonical mid price whenever the oracle spread is non-zero.

The extension's `_metrics()` function uses this inflated mid price to compute per-share LP value:

```solidity
metricT0 = _clampMetric(t0ps + Math.mulDiv(Math.mulDiv(uint256(t1), Q64, midPriceX64), METRIC_SCALE, shares));
metricT1 = _clampMetric(Math.mulDiv(Math.mulDiv(uint256(t0), midPriceX64, Q64), METRIC_SCALE, shares) + t1ps);
``` [3](#0-2) 

Because `midPriceX64_arithmetic > midPriceX64_geometric`:

- `metricT0` is **understated**: the `t1 * Q64 / midPriceX64` term is smaller than it should be.
- `metricT1` is **overstated**: the `t0 * midPriceX64 / Q64` term is larger than it should be.

The watermarks are ratcheted to the live metric values on each swap:

```solidity
(uint256 hwm0, bool breach0) = _applyWatermark(metricT0, _decayed(hwmS.token0, decayRate, dt), floorMultiplier);
if (breach0 && zeroForOne) {
    revert OracleStopLossTriggered(...);
}
(uint256 hwm1, bool breach1) = _applyWatermark(metricT1, _decayed(hwmS.token1, decayRate, dt), floorMultiplier);
if (breach1 && !zeroForOne) {
    revert OracleStopLossTriggered(...);
}
``` [4](#0-3) 

So `hwm0` is anchored too low and `hwm1` too high relative to the pool's canonical mid price.

### Impact Explanation

**Direct LP loss (less protective for `zeroForOne`):** `hwm0` is set below the true geometric-mid value. The drawdown floor `hwm0 * (1 - drawdown)` is therefore lower than intended. A real value leak that should trigger the stop-loss may not, allowing LPs to lose more token1 than the configured drawdown threshold.

**Broken swap flow (over-aggressive for `!zeroForOne`):** `hwm1` is set above the true geometric-mid value. The drawdown floor is higher than intended. A pure oracle mid-price move (no actual value leak) can cause `metricT1` to fall below the inflated floor, reverting legitimate swaps with `OracleStopLossTriggered`.

The magnitude scales with the oracle spread. For a 10% spread (bid = 0.95, ask = 1.05):
- AM = 1.0, GM = sqrt(0.9975) ≈ 0.99875 → ~0.125% error in mid price
- For a 5% drawdown threshold, this is a ~2.5% relative error in the protection floor

For a 50% spread (bid = 0.75, ask = 1.25):
- AM = 1.0, GM ≈ 0.9683 → ~3.2% error in mid price

### Likelihood Explanation

Every pool that deploys `OracleValueStopLossExtension` with a non-zero `drawdownE6` and a non-zero oracle spread is affected on every swap. The trigger is any normal swap — no privileged access or malicious setup required. The oracle spread is always non-zero in production (the `PriceProvider` and `AnchoredPriceProvider` both enforce `bid < ask`). [5](#0-4) 

### Recommendation

Replace the arithmetic mean with the geometric mean, matching the pool's canonical formula:

```solidity
// Before (wrong):
uint256 midPriceX64 = (uint256(bidPriceX64) + uint256(askPriceX64)) / 2;

// After (correct):
uint256 midPriceX64 = Math.sqrt(uint256(bidPriceX64) * uint256(askPriceX64));
```

This aligns the stop-loss extension's mid price with `SwapMath.midAndSpreadFeeX64FromBidAsk`, ensuring LP value metrics are measured at the same price the pool uses for swap execution.

### Proof of Concept

Setup: pool with `OracleValueStopLossExtension`, `drawdownE6 = 50_000` (5%), bid = `0.95 * Q64`, ask = `1.05 * Q64`, bin with `t0 = 1000, t1 = 1000, shares = 10_000`.

**Arithmetic mean (current code):**
- `midPriceX64 = (0.95 + 1.05) / 2 * Q64 = 1.0 * Q64`
- `metricT0 = 1000/10000 + (1000 * Q64 / (1.0 * Q64)) / 10000 = 0.1 + 0.1 = 0.2`
- `hwm0 = 0.2`, floor = `0.2 * 0.95 = 0.19`

**Geometric mean (correct):**
- `midPriceX64 = sqrt(0.95 * 1.05) * Q64 ≈ 0.99875 * Q64`
- `metricT0 = 0.1 + (1000 / 0.99875) / 10000 ≈ 0.1 + 0.10013 = 0.20013`
- `hwm0 = 0.20013`, floor = `0.20013 * 0.95 ≈ 0.19012`

The arithmetic-mean watermark floor (0.19) is lower than the geometric-mean floor (0.19012). A value leak that drops `metricT0` to 0.1901 would correctly trigger the stop-loss with geometric mean but silently pass with arithmetic mean, allowing LPs to lose more than the 5% drawdown threshold.

### Citations

**File:** metric-periphery/contracts/extensions/OracleValueStopLossExtension.sol (L218-218)
```text
    uint256 midPriceX64 = (uint256(bidPriceX64) + uint256(askPriceX64)) / 2;
```

**File:** metric-periphery/contracts/extensions/OracleValueStopLossExtension.sol (L254-255)
```text
    metricT0 = _clampMetric(t0ps + Math.mulDiv(Math.mulDiv(uint256(t1), Q64, midPriceX64), METRIC_SCALE, shares));
    metricT1 = _clampMetric(Math.mulDiv(Math.mulDiv(uint256(t0), midPriceX64, Q64), METRIC_SCALE, shares) + t1ps);
```

**File:** metric-periphery/contracts/extensions/OracleValueStopLossExtension.sol (L270-278)
```text
    (uint256 hwm0, bool breach0) = _applyWatermark(metricT0, _decayed(hwmS.token0, decayRate, dt), floorMultiplier);
    if (breach0 && zeroForOne) {
      revert OracleStopLossTriggered(binIdx, true, metricT0, (hwm0 * floorMultiplier) / E6);
    }

    (uint256 hwm1, bool breach1) = _applyWatermark(metricT1, _decayed(hwmS.token1, decayRate, dt), floorMultiplier);
    if (breach1 && !zeroForOne) {
      revert OracleStopLossTriggered(binIdx, false, metricT1, (hwm1 * floorMultiplier) / E6);
    }
```

**File:** metric-core/contracts/libraries/SwapMath.sol (L70-71)
```text
    midPriceX64 = Math.sqrt(bidPriceX64 * askPriceX64);
    baseFeeX64 = Math.mulDiv(askPriceX64, ONE_X64, midPriceX64, Math.Rounding.Ceil) - ONE_X64;
```

**File:** metric-core/contracts/MetricOmmPool.sol (L806-809)
```text
    try IPriceProvider(activePriceProvider).getBidAndAskPrice() returns (uint128 bid, uint128 ask) {
      if (bid >= ask) revert BidGreaterThanAsk();
      if (bid == 0) revert BidIsZero();
      return (bid, ask);
```
