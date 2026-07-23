### Title
`OracleValueStopLossExtension` High Watermarks Not Reset on Full Bin Liquidity Withdrawal, Causing Permanent False Stop-Loss Triggers - (`metric-periphery/contracts/extensions/OracleValueStopLossExtension.sol`)

---

### Summary

`OracleValueStopLossExtension` tracks per-share value high watermarks (`highWatermarks[pool][binIdx]`) that are updated **only** in `afterSwap`. When all liquidity is removed from a bin (total shares → 0) and new liquidity is subsequently added, the stale watermark from the previous LP epoch is compared against the new (lower) initial per-share metric, triggering a false `OracleStopLossTriggered` revert that permanently blocks swaps through that bin.

---

### Finding Description

`OracleValueStopLossExtension` only overrides `afterSwap` and `initialize` from `BaseMetricExtension`. All other hooks (`afterRemoveLiquidity`, `afterAddLiquidity`, etc.) are not registered for this extension. [1](#0-0) 

The watermark update path is exclusively:

```
swap() → _afterSwap() → afterSwap() → _afterSwapOracleStopLoss() → _checkAndUpdateWatermarks()
``` [2](#0-1) 

`_checkAndUpdateWatermarks` ratchets the watermark up on new highs but never resets it downward except via linear decay. When a bin's total shares reach zero (full withdrawal), the watermark is frozen at its last high value. [3](#0-2) 

When new LPs subsequently add liquidity to the empty bin, `LiquidityLib.addLiquidity` initialises the bin at `INITIAL_SCALED_TOKEN_0_PER_SHARE_E18` / `INITIAL_SCALED_TOKEN_1_PER_SHARE_E18`: [4](#0-3) 

The initial per-share value is typically far below the watermark that was set when the bin had accumulated swap-driven value. On the next swap touching that bin, `afterSwap` fires and computes:

```
metricT0 = t0*SCALE/shares + (t1*Q64/mid)*SCALE/shares   // initial value, low
``` [5](#0-4) 

Since `metricT0 < hwm * floorMultiplier / E6`, `_applyWatermark` sets `breached = true` and the swap reverts with `OracleStopLossTriggered`. [6](#0-5) 

`_afterSwapOracleStopLoss` also skips bins with `totalShares == 0`, so the watermark is never cleared while the bin is empty — it only gets a chance to update when shares are non-zero, at which point the false breach is already detected. [7](#0-6) 

---

### Impact Explanation

Any swap that crosses or touches the affected bin reverts with `OracleStopLossTriggered`. If the affected bin is the current bin (`curBinIdx`), **all swaps in the pool are blocked**. If decay is set to zero (`decayPerSecondE8 = 0`), the block is permanent. Even with decay enabled, recovery requires waiting until the watermark decays below `metric / floorMultiplier`, which can take days to weeks depending on configuration. This constitutes broken core pool functionality causing an unusable swap flow.

---

### Likelihood Explanation

The trigger requires:
1. All shares removed from a bin — permitted by `removeLiquidity` since `newUserShares = 0` is explicitly allowed.
2. New liquidity added to the same bin — a normal LP action.
3. A swap touching that bin — routine. [8](#0-7) 

Bins frequently drain to zero when price moves away from a range (all LPs withdraw an out-of-range bin), then refill when price returns. This is a standard LP lifecycle, making the trigger realistic without any adversarial intent.

---

### Recommendation

Reset the per-bin watermark to zero (or to the current metric) when a bin's total shares reach zero. The cleanest fix is to implement `afterRemoveLiquidity` in `OracleValueStopLossExtension` and, for each bin in the delta whose post-removal total shares equal zero, delete `highWatermarks[pool][binIdx]`. Alternatively, in `_afterSwapOracleStopLoss`, when `totalShares == 0` is detected, explicitly clear the watermark for that bin rather than skipping it.

---

### Proof of Concept

```
Setup: pool with OracleValueStopLossExtension, drawdown=50% (floorMultiplier=500_000), decayPerSecondE8=0

1. LP1 adds 10_000 shares to bin 0 (current bin).
   → bin0: token0=1000, token1=1000, totalShares=10_000

2. Several swaps occur through bin 0.
   → afterSwap fires, watermark set: hwm0 = 2000 (per-share value rose due to swap gains)

3. LP1 removes all 10_000 shares from bin 0.
   → bin0: token0=0, token1=0, totalShares=0
   → highWatermarks[pool][0].token0 = 2000  ← NOT cleared

4. LP2 adds 10_000 shares to bin 0 (empty bin).
   → bin0: token0=initialPerShare*10_000, token1=initialPerShare*10_000
   → e.g. token0=500, token1=500 at initial rate

5. Any swap touching bin 0:
   → afterSwap fires
   → metricT0 = 500*1e6/10_000 + ... ≈ 100
   → hwm0 (decayed) = 2000 (no decay)
   → threshold = 2000 * 500_000 / 1_000_000 = 1000
   → 100 < 1000 → OracleStopLossTriggered revert
   → ALL swaps through bin 0 permanently blocked
``` [2](#0-1) [9](#0-8)

### Citations

**File:** metric-periphery/contracts/extensions/OracleValueStopLossExtension.sol (L185-204)
```text
  function afterSwap(
    address,
    address,
    bool zeroForOne,
    int128,
    uint128,
    uint256 packedSlot0Initial,
    uint256 packedSlot0Final,
    uint128 bidPriceX64,
    uint128 askPriceX64,
    int128,
    int128,
    uint256,
    bytes calldata
  ) external override returns (bytes4) {
    // Only the factory can initialize, so an initialized msg.sender is a legit pool — no onlyPool needed.
    _requireInitialized(msg.sender);
    _afterSwapOracleStopLoss(msg.sender, packedSlot0Initial, packedSlot0Final, bidPriceX64, askPriceX64, zeroForOne);
    return IMetricOmmExtensions.afterSwap.selector;
  }
```

**File:** metric-periphery/contracts/extensions/OracleValueStopLossExtension.sol (L236-242)
```text
    for (uint256 i = 0; i < count; i++) {
      uint256 totalShares = PoolStateLibrary._decodeBinTotalShares(shares[i]);
      if (totalShares == 0) continue;
      (uint104 t0, uint104 t1,,,) = PoolStateLibrary._decodeBinState(states[i]);
      (uint256 metricT0, uint256 metricT1) = _metrics(t0, t1, totalShares, minShares, midPriceX64);
      _checkAndUpdateWatermarks(pool_, binIdxs[i], metricT0, metricT1, floorMultiplier, decayRate, zeroForOne);
    }
```

**File:** metric-periphery/contracts/extensions/OracleValueStopLossExtension.sol (L246-256)
```text
  function _metrics(uint104 t0, uint104 t1, uint256 totalShares, uint256 minShares, uint256 midPriceX64)
    private
    pure
    returns (uint256 metricT0, uint256 metricT1)
  {
    uint256 shares = totalShares < minShares ? minShares : totalShares;
    uint256 t0ps = Math.mulDiv(uint256(t0), METRIC_SCALE, shares);
    uint256 t1ps = Math.mulDiv(uint256(t1), METRIC_SCALE, shares);
    metricT0 = _clampMetric(t0ps + Math.mulDiv(Math.mulDiv(uint256(t1), Q64, midPriceX64), METRIC_SCALE, shares));
    metricT1 = _clampMetric(Math.mulDiv(Math.mulDiv(uint256(t0), midPriceX64, Q64), METRIC_SCALE, shares) + t1ps);
  }
```

**File:** metric-periphery/contracts/extensions/OracleValueStopLossExtension.sol (L258-285)
```text
  function _checkAndUpdateWatermarks(
    address pool_,
    int8 binIdx,
    uint256 metricT0,
    uint256 metricT1,
    uint256 floorMultiplier,
    uint256 decayRate,
    bool zeroForOne
  ) private {
    BinHighWatermarks storage hwmS = highWatermarks[pool_][binIdx];
    uint256 dt = block.timestamp - hwmS.lastDecayTs;

    (uint256 hwm0, bool breach0) = _applyWatermark(metricT0, _decayed(hwmS.token0, decayRate, dt), floorMultiplier);
    if (breach0 && zeroForOne) {
      revert OracleStopLossTriggered(binIdx, true, metricT0, (hwm0 * floorMultiplier) / E6);
    }

    (uint256 hwm1, bool breach1) = _applyWatermark(metricT1, _decayed(hwmS.token1, decayRate, dt), floorMultiplier);
    if (breach1 && !zeroForOne) {
      revert OracleStopLossTriggered(binIdx, false, metricT1, (hwm1 * floorMultiplier) / E6);
    }

    // forge-lint: disable-next-line(unsafe-typecast)
    hwmS.token0 = uint104(hwm0);
    // forge-lint: disable-next-line(unsafe-typecast)
    hwmS.token1 = uint104(hwm1);
    hwmS.lastDecayTs = uint32(block.timestamp);
  }
```

**File:** metric-periphery/contracts/extensions/OracleValueStopLossExtension.sol (L326-336)
```text
  /// @dev Ratchet up on new highs; report breach below the drawdown floor. Direction-aware
  ///      blocking is decided by the caller.
  function _applyWatermark(uint256 metric, uint256 hwm, uint256 floorMultiplier)
    private
    pure
    returns (uint256 newHwm, bool breached)
  {
    if (metric >= hwm) return (metric, false);
    breached = metric < (hwm * floorMultiplier) / E6;
    return (hwm, breached);
  }
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L85-111)
```text
          if (binTotalSharesVal == 0) {
            if (binIdx < curBinIdxCache) {
              amount1Scaled = Math.ceilDiv(_checkedMul(ctx.initialScaledToken1PerShareE18, sharesToAdd), 1e18);
            } else if (binIdx > curBinIdxCache) {
              amount0Scaled = Math.ceilDiv(_checkedMul(ctx.initialScaledToken0PerShareE18, sharesToAdd), 1e18);
            } else {
              uint256 token0Proportion = type(uint104).max - ctx.curPosInBin;
              uint256 token1Proportion = ctx.curPosInBin;
              amount0Scaled =
              (Math.mulDiv(
                  token0Proportion * ctx.initialScaledToken0PerShareE18,
                  sharesToAdd,
                  uint256(type(uint104).max) * 1e18,
                  Math.Rounding.Ceil
                ));
              amount1Scaled =
              (Math.mulDiv(
                  token1Proportion * ctx.initialScaledToken1PerShareE18,
                  sharesToAdd,
                  uint256(type(uint104).max) * 1e18,
                  Math.Rounding.Ceil
                ));
            }
          } else {
            amount0Scaled = Math.ceilDiv(_checkedMul(binState.token0BalanceScaled, sharesToAdd), binTotalSharesVal);
            amount1Scaled = Math.ceilDiv(_checkedMul(binState.token1BalanceScaled, sharesToAdd), binTotalSharesVal);
          }
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L161-214)
```text
  function removeLiquidity(
    PoolContext memory ctx,
    address owner,
    uint80 salt,
    LiquidityDelta calldata deltas,
    BinTotals storage binTotals,
    mapping(int256 => BinState) storage binStates,
    mapping(int256 => uint256) storage binTotalShares,
    mapping(bytes32 => uint256) storage positionBinShares
  ) public returns (uint256 amount0Removed, uint256 amount1Removed) {
    unchecked {
      uint256 length = deltas.binIdxs.length;
      if (length == 0) return (0, 0);

      uint256 totalToken0ToRemoveScaled = 0;
      uint256 totalToken1ToRemoveScaled = 0;

      BinBalanceDelta[] memory binBalanceDeltas = new BinBalanceDelta[](length);

      for (uint256 i = 0; i < length; i++) {
        int256 binIdx = deltas.binIdxs[i];
        uint256 sharesToRemove = deltas.shares[i];

        if (binIdx < ctx.lowestBin || binIdx > ctx.highestBin) {
          revert IMetricOmmPoolActions.InvalidBinIndex(binIdx);
        }
        if (sharesToRemove == 0) continue;

        {
          // safe because -128 <= LOWEST_BIN <= HIGHEST_BIN <= 127 (enforced by factory)
          // forge-lint: disable-next-line(unsafe-typecast)
          bytes32 posKey = _positionBinKey(owner, salt, int8(binIdx));
          uint256 binTotalSharesVal = binTotalShares[binIdx];
          uint256 userShares = positionBinShares[posKey];

          if (userShares < sharesToRemove) {
            revert IMetricOmmPoolActions.InsufficientLiquidity(sharesToRemove, userShares);
          }
          uint256 newUserShares = userShares - sharesToRemove;
          if (newUserShares > 0 && newUserShares < ctx.minimalMintableLiquidity) {
            revert IMetricOmmPoolActions.MinimalLiquidity(newUserShares, ctx.minimalMintableLiquidity);
          }

          BinState storage binState = binStates[binIdx];
          uint256 amount0Scaled = _checkedMul(binState.token0BalanceScaled, sharesToRemove) / binTotalSharesVal;
          uint256 amount1Scaled = _checkedMul(binState.token1BalanceScaled, sharesToRemove) / binTotalSharesVal;

          // casting to uint104 is safe because amount0Scaled and amount1Scaled are less than token(0|1)BalanceScaled
          // forge-lint: disable-next-line(unsafe-typecast)
          binState.token0BalanceScaled -= uint104(amount0Scaled);
          // forge-lint: disable-next-line(unsafe-typecast)
          binState.token1BalanceScaled -= uint104(amount1Scaled);
          binTotalShares[binIdx] = binTotalSharesVal - sharesToRemove;
          positionBinShares[posKey] = newUserShares;
```
