Audit Report

## Title
`OracleValueStopLossExtension` High Watermarks Not Reset on Full Bin Liquidity Withdrawal, Causing Permanent False Stop-Loss Triggers - (`metric-periphery/contracts/extensions/OracleValueStopLossExtension.sol`)

## Summary

`OracleValueStopLossExtension` stores per-bin high watermarks (`highWatermarks[pool][binIdx]`) that are updated exclusively in `afterSwap`. When all liquidity is removed from a bin (total shares → 0) and new liquidity is subsequently added, the stale watermark from the previous LP epoch is compared against the new (lower) initial per-share metric, triggering a false `OracleStopLossTriggered` revert that permanently blocks swaps through that bin when `decayPerSecondE8 = 0`.

## Finding Description

`OracleValueStopLossExtension` only overrides `afterSwap` and `initialize` from `BaseMetricExtension`. All other hooks (`afterRemoveLiquidity`, `afterAddLiquidity`, etc.) revert with `ExtensionNotImplemented()` in the base, so the extension cannot be registered for those hooks.

The watermark update path is exclusively:
```
swap() → _afterSwap() → afterSwap() → _afterSwapOracleStopLoss() → _checkAndUpdateWatermarks()
```

In `_afterSwapOracleStopLoss`, bins with `totalShares == 0` are explicitly skipped:

```solidity
if (totalShares == 0) continue;
```

This means when a bin drains to zero shares, the watermark is frozen at its last high value and never cleared.

When new LPs add liquidity to the empty bin, `LiquidityLib.addLiquidity` initialises the bin at `initialScaledToken0PerShareE18` / `initialScaledToken1PerShareE18` — a fixed initial rate set at pool creation. The resulting per-share metric is typically far below the watermark accumulated during the previous LP epoch.

On the next swap touching that bin, `afterSwap` fires, computes the low initial metric, and `_applyWatermark` evaluates:

```solidity
breached = metric < (hwm * floorMultiplier) / E6;
```

Since `metric < hwm * floorMultiplier / E6`, `breached = true` and the swap reverts with `OracleStopLossTriggered`. The only admin escape hatch — `executeOracleStopLossHighWatermarks` — requires a timelock and is a trusted action, not available to unprivileged users.

## Impact Explanation

Any swap crossing or touching the affected bin reverts with `OracleStopLossTriggered`. If the affected bin is the current bin (`curBinIdx`), all swaps in the pool are blocked. When `decayPerSecondE8 = 0`, the block is permanent with no unprivileged recovery path. Even with decay enabled, recovery requires waiting until the watermark decays below `metric / floorMultiplier`, which can take days to weeks. This constitutes broken core pool functionality causing an unusable swap flow.

## Likelihood Explanation

The trigger requires three routine, non-adversarial LP lifecycle events:
1. All shares removed from a bin — permitted by `removeLiquidity` since `newUserShares = 0` is explicitly allowed.
2. New liquidity added to the same bin — a normal LP action.
3. A swap touching that bin — routine.

Bins frequently drain to zero when price moves away from a range (all LPs withdraw an out-of-range bin), then refill when price returns. No adversarial intent is required.

## Recommendation

Reset the per-bin watermark to zero (or to the current metric) when a bin's total shares reach zero. The cleanest fix is to implement `afterRemoveLiquidity` in `OracleValueStopLossExtension` and, for each bin in the delta whose post-removal total shares equal zero, `delete highWatermarks[pool][binIdx]`. Alternatively, in `_afterSwapOracleStopLoss`, when `totalShares == 0` is detected, explicitly clear the watermark for that bin rather than skipping it.

## Proof of Concept

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
   → LiquidityLib initialises at initialScaledToken0PerShareE18
   → bin0: token0=500, token1=500 at initial rate

5. Any swap touching bin 0:
   → afterSwap fires
   → metricT0 ≈ 100 (500*1e6/10_000 + ...)
   → hwm0 (no decay) = 2000
   → threshold = 2000 * 500_000 / 1_000_000 = 1000
   → 100 < 1000 → OracleStopLossTriggered revert
   → ALL swaps through bin 0 permanently blocked
```