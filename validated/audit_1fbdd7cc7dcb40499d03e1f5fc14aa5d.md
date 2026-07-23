Audit Report

## Title
`OracleValueStopLossExtension` High Watermarks Not Reset on Full Bin Liquidity Withdrawal, Causing Permanent False Stop-Loss Triggers - (`metric-periphery/contracts/extensions/OracleValueStopLossExtension.sol`)

## Summary

`OracleValueStopLossExtension` maintains per-bin high watermarks (`highWatermarks[pool][binIdx]`) that are updated exclusively in `afterSwap`. When all shares are removed from a bin, the watermark is frozen at its last high value. When new liquidity is subsequently added to the empty bin, the initial per-share metric is far below the stale watermark, causing `_applyWatermark` to report a breach and revert every subsequent swap touching that bin with `OracleStopLossTriggered`. With `decayPerSecondE8 = 0`, this block is permanent.

## Finding Description

The watermark update path is exclusively `afterSwap → _afterSwapOracleStopLoss → _checkAndUpdateWatermarks`. In `_afterSwapOracleStopLoss`, bins with `totalShares == 0` are skipped via `continue` rather than having their watermarks cleared:

```solidity
// OracleValueStopLossExtension.sol L236-238
uint256 totalShares = PoolStateLibrary._decodeBinTotalShares(shares[i]);
if (totalShares == 0) continue;
```

This means when all LP shares are removed from a bin (reducing `binTotalShares[binIdx]` to zero in `LiquidityLib.removeLiquidity`), the `highWatermarks[pool][binIdx]` entry retains its last ratcheted value indefinitely.

When new LPs subsequently add liquidity to the empty bin, `LiquidityLib.addLiquidity` initialises the bin at `initialScaledToken0PerShareE18` / `initialScaledToken1PerShareE18` (a fixed initial rate set at pool creation), which is typically far below the accumulated per-share value from the previous LP epoch's swap gains.

On the next swap touching that bin, `afterSwap` fires with `totalShares > 0`, computes a low `metricT0`/`metricT1`, and calls `_checkAndUpdateWatermarks`. Inside `_applyWatermark`:

```solidity
// OracleValueStopLossExtension.sol L333-335
if (metric >= hwm) return (metric, false);
breached = metric < (hwm * floorMultiplier) / E6;
return (hwm, breached);
```

Since `metric << hwm` (initial value vs. accumulated watermark), `breached = true`. `_checkAndUpdateWatermarks` then reverts before updating storage:

```solidity
// OracleValueStopLossExtension.sol L271-273
if (breach0 && zeroForOne) {
  revert OracleStopLossTriggered(binIdx, true, metricT0, (hwm0 * floorMultiplier) / E6);
}
```

Because the revert occurs before `hwmS.token0/token1/lastDecayTs` are written, the stale watermark persists across every subsequent swap attempt, making the block self-perpetuating. `OracleValueStopLossExtension` does not override `afterRemoveLiquidity` — the base implementation reverts with `ExtensionNotImplemented()`, so the pool deployer cannot register this extension for that hook without breaking all removals.

## Impact Explanation

Any swap crossing or touching the affected bin reverts with `OracleStopLossTriggered`. If the affected bin is the current active bin (`curBinIdx`), all swaps in the pool are blocked. With `decayPerSecondE8 = 0`, the block is permanent. Even with decay enabled, recovery requires waiting until the watermark decays below `metric / floorMultiplier`, which can take days to weeks. This constitutes broken core pool functionality — the swap flow is rendered unusable — meeting the "Broken core pool functionality causing loss of funds or unusable withdraw/swap/liquidity flows" impact criterion.

## Likelihood Explanation

The trigger requires three standard, unprivileged LP/trader actions: (1) full withdrawal of all shares from a bin (permitted by `removeLiquidity` since `newUserShares = 0` is explicitly allowed at `LiquidityLib.sol` L199-202), (2) new liquidity added to the same bin (normal LP action), and (3) a swap touching that bin (routine). Bins draining to zero is a standard LP lifecycle event when price moves out of range and all LPs withdraw; this is not adversarial and occurs in normal pool operation.

## Recommendation

Reset the per-bin watermark to zero when a bin's total shares reach zero. The cleanest fix is to implement `afterRemoveLiquidity` in `OracleValueStopLossExtension`: for each bin in the delta whose post-removal `binTotalShares` equals zero, `delete highWatermarks[pool][binIdx]`. Alternatively, in `_afterSwapOracleStopLoss`, replace the `continue` for `totalShares == 0` bins with an explicit watermark deletion: `delete highWatermarks[pool_][binIdxs[i]]`.

## Proof of Concept

```
Setup: pool with OracleValueStopLossExtension, drawdown=50% (floorMultiplier=500_000), decayPerSecondE8=0

1. LP1 adds 10_000 shares to bin 0 (current bin).
   → bin0: token0=1000, token1=1000, totalShares=10_000

2. Several swaps occur through bin 0.
   → afterSwap fires, watermark set: hwm0 = 2000 (per-share value rose due to swap gains)

3. LP1 removes all 10_000 shares from bin 0.
   → bin0: token0=0, token1=0, totalShares=0
   → highWatermarks[pool][0].token0 = 2000  ← NOT cleared (bin skipped in afterSwap loop)

4. LP2 adds 10_000 shares to bin 0 (empty bin).
   → LiquidityLib.addLiquidity initialises at initialScaledToken0PerShareE18
   → bin0: token0=500, token1=500 at initial rate

5. Any swap touching bin 0:
   → afterSwap fires, totalShares=10_000 (non-zero, not skipped)
   → metricT0 = 500*1e6/10_000 + ... ≈ 100
   → hwm0 (no decay) = 2000
   → threshold = 2000 * 500_000 / 1_000_000 = 1000
   → 100 < 1000 → OracleStopLossTriggered revert
   → revert occurs before hwmS is updated → watermark stays at 2000
   → ALL subsequent swaps through bin 0 permanently blocked
```