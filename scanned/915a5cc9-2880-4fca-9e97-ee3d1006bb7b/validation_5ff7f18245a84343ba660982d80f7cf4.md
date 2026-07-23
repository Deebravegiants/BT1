After a thorough investigation of the Metric OMM codebase, I traced every path the external bug class could manifest through.

**Price limit comparison** (`priceLimitX64` vs internal bin prices): All comparisons are in Q64.64 format on both sides. `priceLimitX64` is passed directly as `uint128` and compared to `lowerPriceX64`, `upperPriceX64`, and `initialPriceX64`, all derived from the same Q64.64 oracle mid-price. No unit mismatch exists here. [1](#0-0) [2](#0-1) 

**Token scaling path**: `amountSpecified` (native units) is correctly multiplied by `TOKEN_X_SCALE_MULTIPLIER` before entering bin math. The oracle price is in real-world ratio units (e.g., USDC per ETH), which equals the internal scaled ratio since both tokens are normalized to the same internal precision (`max(18, decimals)`). No cross-unit comparison occurs. [3](#0-2) [4](#0-3) 

**`IncorrectDelta` callback check**: `amount0Delta`/`amount1Delta` are converted to native units via `deltasScaledToExternal` before the balance check. `balance0()` and `balance1()` return native ERC-20 balances. All operands are in native units. [5](#0-4) [6](#0-5) 

**`collectFees` surplus calculation**: `balance0() * TOKEN_0_SCALE_MULTIPLIER`, `binTotals.scaledToken0`, and `notionalFeeToken0Scaled` are all in scaled units. The subtraction is unit-consistent. [7](#0-6) 

**Notional fee accounting**: Bin totals are updated using `amount1DeltaScaled` (scaled units) *before* the notional fee modifier is applied. The notional fee accumulator `notionalFeeToken1Scaled` is also in scaled units. The surplus identity `balance_scaled - binTotals - notionalFee = rounding_dust ≥ 0` holds correctly. [8](#0-7) 
<cite repo="Alyssadaypin/2026

### Citations

**File:** metric-core/contracts/MetricOmmPool.sol (L48-51)
```text
  /// @notice Multiplier to scale token0 external amounts to internal: 10^(max(18, decimals) - token0.decimals())
  uint256 internal immutable TOKEN_0_SCALE_MULTIPLIER;
  /// @notice Multiplier to scale token1 external amounts to internal: 10^(max(18, decimals) - token1.decimals())
  uint256 internal immutable TOKEN_1_SCALE_MULTIPLIER;
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

**File:** metric-core/contracts/MetricOmmPool.sol (L385-388)
```text
    uint256 surplus0Scaled =
      balance0() * TOKEN_0_SCALE_MULTIPLIER - uint256(binTotals.scaledToken0) - notionalFee0AmountScaled;
    uint256 surplus1Scaled =
      balance1() * TOKEN_1_SCALE_MULTIPLIER - uint256(binTotals.scaledToken1) - notionalFee1AmountScaled;
```

**File:** metric-core/contracts/MetricOmmPool.sol (L607-614)
```text
  function deltasScaledToExternal(int256 scaledDeltaAmount0, int256 scaledDeltaAmount1)
    internal
    view
    returns (int256 deltaAmount0, int256 deltaAmount1)
  {
    deltaAmount0 = SignedMath.ceilDiv(scaledDeltaAmount0, TOKEN_0_SCALE_MULTIPLIER);
    deltaAmount1 = SignedMath.ceilDiv(scaledDeltaAmount1, TOKEN_1_SCALE_MULTIPLIER);
  }
```

**File:** metric-core/contracts/MetricOmmPool.sol (L683-704)
```text
      if (amountSpecified > 0) {
        if (zeroForOne) {
          // forge-lint: disable-next-line(unsafe-typecast)
          uint256 amountInScaled = TOKEN_0_SCALE_MULTIPLIER * uint256(amountSpecified);
          uint256 amountOutScaled;
          (amountInScaled, amountOutScaled, protocolFeeScaled) =
            _swapToken0ForToken1SpecifiedInput(amountInScaled, params);
          // forge-lint: disable-next-line(unsafe-typecast)
          amount0DeltaScaled = int256(amountInScaled);
          // forge-lint: disable-next-line(unsafe-typecast)
          amount1DeltaScaled = -int256(amountOutScaled);
        } else {
          // forge-lint: disable-next-line(unsafe-typecast)
          uint256 amountInScaled = TOKEN_1_SCALE_MULTIPLIER * uint256(amountSpecified);
          uint256 amountOutScaled;
          (amountInScaled, amountOutScaled, protocolFeeScaled) =
            _swapToken1ForToken0SpecifiedInput(amountInScaled, params);
          // forge-lint: disable-next-line(unsafe-typecast)
          amount0DeltaScaled = -int256(amountOutScaled);
          // forge-lint: disable-next-line(unsafe-typecast)
          amount1DeltaScaled = int256(amountInScaled);
        }
```

**File:** metric-core/contracts/MetricOmmPool.sol (L732-748)
```text
      if (zeroForOne) {
        // casting to uint256 is safe because amount0DeltaScaled is positive in zeroForOne flow.
        // forge-lint: disable-next-line(unsafe-typecast)
        binTotals.scaledToken0 =
          (uint256(binTotals.scaledToken0) + uint256(amount0DeltaScaled) - protocolFeeScaled).toUint128(); // forge-lint: disable-line(unsafe-typecast)
        // casting to uint128/uint256 is safe because bin totals remain bounded by uint128-scaled accounting invariants.
        // forge-lint: disable-next-line(unsafe-typecast)
        binTotals.scaledToken1 = uint128(uint256(binTotals.scaledToken1) - uint256(-amount1DeltaScaled));
      } else {
        // casting to uint256 is safe because amount1DeltaScaled is positive in !zeroForOne flow.
        // forge-lint: disable-next-line(unsafe-typecast)
        binTotals.scaledToken1 =
          (uint256(binTotals.scaledToken1) + uint256(amount1DeltaScaled) - protocolFeeScaled).toUint128(); // forge-lint: disable-line(unsafe-typecast)
        // casting to uint128/uint256 is safe because bin totals remain bounded by uint128-scaled accounting invariants.
        // forge-lint: disable-next-line(unsafe-typecast)
        binTotals.scaledToken0 = uint128(uint256(binTotals.scaledToken0) - uint256(-amount0DeltaScaled));
      }
```

**File:** metric-core/contracts/MetricOmmPool.sol (L888-890)
```text
      if (params.priceLimitX64 <= initialPriceX64) {
        return (0, 0, 0, 0);
      }
```

**File:** metric-core/contracts/MetricOmmPool.sol (L970-972)
```text
      if (params.priceLimitX64 <= initialPriceX64) {
        return (0, 0, 0);
      }
```
