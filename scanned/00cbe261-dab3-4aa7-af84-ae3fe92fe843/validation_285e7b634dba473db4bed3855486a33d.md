### Title
Missing Minimum Output Protection in `removeLiquidity` Exposes LPs to Front-Running Composition Drain — (File: `metric-core/contracts/MetricOmmPool.sol`)

---

### Summary

`MetricOmmPool.removeLiquidity` accepts no minimum-output parameters (`minAmount0`, `minAmount1`). There is no periphery wrapper for remove-liquidity that adds such a guard. A front-runner can swap to shift the cursor within the target bin immediately before the LP's transaction, causing the LP to receive a skewed token composition — and potentially a lower total value — with no on-chain recourse.

---

### Finding Description

`removeLiquidity` in `MetricOmmPool.sol` has the following signature:

```solidity
function removeLiquidity(
    address owner,
    uint80 salt,
    LiquidityDelta calldata deltas,
    bytes calldata extensionData
) external nonReentrant(PoolActions.REMOVE_LIQUIDITY)
  returns (uint256 amount0Removed, uint256 amount1Removed)
``` [1](#0-0) 

There are no `minAmount0` or `minAmount1` parameters. The function delegates directly to `LiquidityLib.removeLiquidity`, which computes token amounts from the current bin state (`_binStates`, `_binTotalShares`, `_positionBinShares`) at execution time. [2](#0-1) 

The periphery layer (`MetricOmmPoolLiquidityAdder.sol`) only wraps **add-liquidity** operations. There is no `MetricOmmPoolLiquidityRemover` or equivalent contract that wraps `removeLiquidity` with slippage guards.



By contrast, `addLiquidityExactShares` and `addLiquidityWeighted` both enforce `maxAmountToken0` / `maxAmountToken1` caps in the callback, and `addLiquidityWeighted` additionally validates cursor bounds via `_validateBinAndBinPosition`: [3](#0-2) [4](#0-3) 

No analogous protection exists for the remove path.

**Attack scenario:**

1. LP submits `removeLiquidity` targeting bin `k` with `N` shares.
2. Attacker observes the pending transaction in the mempool.
3. Attacker front-runs with a swap that moves `curPosInBin` to the extreme of bin `k` (e.g., fully toward token1), draining token0 from that bin.
4. LP's transaction executes: `LiquidityLib.removeLiquidity` reads the now-skewed bin state and returns mostly token1, little token0.
5. LP receives a composition they did not intend and must swap to rebalance, paying the spread fee again.

The spread fee is charged on the attacker's swap and flows to the protocol/admin — **not** to the LP — so the LP receives no compensation for the composition shift. [5](#0-4) 

---

### Impact Explanation

LPs removing liquidity from a specific bin can receive a materially different token ratio than expected. Because the pool is oracle-based, the total value at oracle prices is approximately preserved, but:

- The LP may receive a token they did not want, forcing an additional swap at spread cost.
- For large positions or wide bins, the composition skew can be significant.
- The attacker profits indirectly by sandwiching (swap before + swap after the LP's remove), capturing the spread on both legs while the LP bears the rebalancing cost.

This constitutes a medium direct loss of LP assets above typical Sherlock thresholds when position sizes are non-trivial.

---

### Likelihood Explanation

- `removeLiquidity` is a public, unprivileged call (only `msg.sender == owner` is required, so any LP can be targeted).
- Front-running is standard on EVM chains with a public mempool.
- No existing on-chain guard prevents the attack.

---

### Recommendation

1. **Add minimum output parameters** to `removeLiquidity`:

```solidity
function removeLiquidity(
    address owner,
    uint80 salt,
    LiquidityDelta calldata deltas,
    uint256 minAmount0,   // <-- add
    uint256 minAmount1,   // <-- add
    bytes calldata extensionData
) external ... returns (uint256 amount0Removed, uint256 amount1Removed) {
    ...
    if (amount0Removed < minAmount0 || amount1Removed < minAmount1)
        revert InsufficientOutput(amount0Removed, amount1Removed, minAmount0, minAmount1);
}
```

2. **Alternatively**, create a `MetricOmmPoolLiquidityRemover` periphery contract (mirroring `MetricOmmPoolLiquidityAdder`) that wraps `removeLiquidity` with post-execution minimum checks, following the same pattern as Uniswap V2's `removeLiquidity` with `amountAMin`/`amountBMin`.

3. **Additionally**, add a cursor-bounds check (analogous to `_validateBinAndBinPosition` used in `addLiquidityWeighted`) to the remove path so that if the pool cursor has been manipulated outside an acceptable range, the transaction reverts before any state change.

---

### Proof of Concept

```
Setup:
  - Pool with token0/token1, bin 0 holds 1000 token0 and 1000 token1 (balanced cursor).
  - LP holds 500 shares in bin 0 and submits removeLiquidity(owner, salt, {binIdxs:[0], shares:[500]}, "").
  - Expected: ~500 token0 + ~500 token1.

Attack:
  1. Attacker sees LP's pending tx.
  2. Attacker swaps a large amount of token1 → token0, moving curPosInBin to near type(uint104).max.
     Bin 0 now holds ~50 token0 and ~1950 token1.
  3. LP's removeLiquidity executes. LiquidityLib computes shares proportional to current bin state:
     LP receives ~25 token0 + ~975 token1 instead of ~500 + ~500.
  4. LP must swap ~475 token1 → token0 at spread cost to restore desired position.
  5. Attacker swaps back (token0 → token1) after LP's tx, profiting from the round-trip spread.

Result: LP loses approximately 2× spread fee on ~475 tokens of rebalancing volume.
No on-chain check reverts the LP's transaction despite the skewed output.
```

### Citations

**File:** metric-core/contracts/MetricOmmPool.sol (L199-212)
```text
  function removeLiquidity(address owner, uint80 salt, LiquidityDelta calldata deltas, bytes calldata extensionData)
    external
    nonReentrant(PoolActions.REMOVE_LIQUIDITY)
    returns (uint256 amount0Removed, uint256 amount1Removed)
  {
    if (deltas.binIdxs.length == 0) return (0, 0);
    if (deltas.binIdxs.length != deltas.shares.length) revert LiquidityDeltaLengthMismatch();
    if (msg.sender != owner) revert NotPositionOwner();
    _beforeRemoveLiquidity(msg.sender, owner, salt, deltas, extensionData);
    (amount0Removed, amount1Removed) = LiquidityLib.removeLiquidity(
      _liquidityContext(), owner, salt, deltas, binTotals, _binStates, _binTotalShares, _positionBinShares
    );
    _afterRemoveLiquidity(msg.sender, owner, salt, deltas, amount0Removed, amount1Removed, extensionData);
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

**File:** metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol (L165-167)
```text
    if (amount0Delta > max0 || amount1Delta > max1) {
      revert MaxAmountExceeded(amount0Delta, amount1Delta, max0, max1);
    }
```

**File:** metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol (L263-286)
```text
  function _validateBinAndBinPosition(
    address pool,
    int8 minimalCurBin,
    uint104 minimalPosition,
    int8 maximalCurBin,
    uint104 maximalPosition
  ) internal view {
    if (minimalCurBin > maximalCurBin) {
      revert CursorOutOfBounds(0, 0, minimalCurBin, minimalPosition, maximalCurBin, maximalPosition);
    }

    (, int8 curBinIdx, uint104 curPosInBin,,,) = PoolStateLibrary._slot0(pool);

    int256 curBin = curBinIdx;
    if (curBin < minimalCurBin || curBin > maximalCurBin) {
      revert CursorOutOfBounds(curBinIdx, curPosInBin, minimalCurBin, minimalPosition, maximalCurBin, maximalPosition);
    }
    if (curBinIdx == minimalCurBin && curPosInBin < minimalPosition) {
      revert CursorOutOfBounds(curBinIdx, curPosInBin, minimalCurBin, minimalPosition, maximalCurBin, maximalPosition);
    }
    if (curBinIdx == maximalCurBin && curPosInBin > maximalPosition) {
      revert CursorOutOfBounds(curBinIdx, curPosInBin, minimalCurBin, minimalPosition, maximalCurBin, maximalPosition);
    }
  }
```
