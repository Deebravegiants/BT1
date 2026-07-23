### Title
No Slippage Protection in `removeLiquidity` Exposes LPs to Front-Running Token Composition Losses — (`metric-core/contracts/MetricOmmPool.sol`, `metric-core/contracts/libraries/LiquidityLib.sol`)

---

### Summary

`removeLiquidity` in `MetricOmmPool.sol` accepts only a share-burn quantity per bin and returns whatever token amounts the bin currently holds proportionally. There is no `minAmount0Out` / `minAmount1Out` guard. Because every `swap` call directly mutates `binState.token0BalanceScaled` and `binState.token1BalanceScaled` before the LP's pending removal executes, a swap front-running the removal changes the token composition the LP receives with no on-chain protection. The periphery `MetricOmmPoolLiquidityAdder` provides `maxAmountToken0` / `maxAmountToken1` caps for `addLiquidity` but exposes no equivalent wrapper for `removeLiquidity`, leaving the removal path entirely unguarded.

---

### Finding Description

**Token-out calculation in `LiquidityLib.removeLiquidity`:**

```solidity
uint256 amount0Scaled = _checkedMul(binState.token0BalanceScaled, sharesToRemove) / binTotalSharesVal;
uint256 amount1Scaled = _checkedMul(binState.token1BalanceScaled, sharesToRemove) / binTotalSharesVal;
``` [1](#0-0) 

Both `token0BalanceScaled` and `token1BalanceScaled` are live storage values that every swap modifies in the same transaction:

```solidity
// zeroForOne swap: token0 enters bins, token1 leaves
binTotals.scaledToken0 = (uint256(binTotals.scaledToken0) + uint256(amount0DeltaScaled) - protocolFeeScaled).toUint128();
binTotals.scaledToken1 = uint128(uint256(binTotals.scaledToken1) - uint256(-amount1DeltaScaled));
``` [2](#0-1) 

And at the per-bin level inside `SwapMath`:

```solidity
binState.token0BalanceScaled -= out0Scaled.toUint104();
binState.token1BalanceScaled = uint256((binState.token1BalanceScaled) + totalIn1Scaled - protocolFeeAmountScaled).toUint104();
``` [3](#0-2) 

**`removeLiquidity` interface — no min-out parameters:**

```solidity
function removeLiquidity(address owner, uint80 salt, LiquidityDelta calldata deltas, bytes calldata extensionData)
    external
    returns (uint256 amount0Removed, uint256 amount1Removed);
``` [4](#0-3) 

The pool-level implementation mirrors this — no guard after the library call:

```solidity
(amount0Removed, amount1Removed) = LiquidityLib.removeLiquidity(
    _liquidityContext(), owner, salt, deltas, binTotals, _binStates, _binTotalShares, _positionBinShares
);
_afterRemoveLiquidity(msg.sender, owner, salt, deltas, amount0Removed, amount1Removed, extensionData);
``` [5](#0-4) 

**Periphery asymmetry:** `MetricOmmPoolLiquidityAdder` provides `maxAmountToken0` / `maxAmountToken1` caps for `addLiquidity` and reverts with `MaxAmountExceeded` if the pool requests more:

```solidity
if (amount0Delta > max0 || amount1Delta > max1) {
    revert MaxAmountExceeded(amount0Delta, amount1Delta, max0, max1);
}
``` [6](#0-5) 

No equivalent periphery contract exists for `removeLiquidity`. Because `removeLiquidity` enforces `msg.sender == owner`, the LP must call the pool directly and cannot route through a slippage-checking wrapper. [7](#0-6) 

---

### Impact Explanation

An LP removing liquidity from a bin that holds both tokens can be sandwich-attacked:

1. Attacker observes the pending `removeLiquidity` targeting bin `B` which holds `T0` token0 and `T1` token1.
2. Attacker front-runs with a swap that drains token0 from bin `B` (paying the ask spread).
3. LP's `removeLiquidity` executes: `token0BalanceScaled` is now near zero, so `amount0Removed ≈ 0` and `amount1Removed` is inflated.
4. Attacker back-runs, buying back token0 at the bid price.

The LP receives the correct *proportional share of the current bin state*, but the composition has been adversarially shifted. If token0 is more valuable than token1 at the oracle price, the LP suffers a direct loss of principal relative to what they would have received without the front-run. The attacker's cost is the bid-ask spread paid twice; on pools with tight spreads (e.g., stablecoin pairs) this attack is profitable.

The loss is bounded by the bin's full token0 balance times the LP's share fraction — for a large LP in a concentrated bin this can be material.

---

### Likelihood Explanation

- Any swap can be used as the front-run vehicle; no special privilege is required.
- The attack is most profitable on pools with small bid-ask spreads and concentrated single-bin LP positions.
- The LP has no on-chain mechanism to prevent it: `removeLiquidity` is called directly by the owner with no deadline, no min-out, and no periphery wrapper.
- Likelihood is **Medium**: requires mempool visibility and a profitable spread condition, but no protocol-level barrier exists.

---

### Recommendation

1. Add `minAmount0Out` and `minAmount1Out` parameters to `removeLiquidity` in both `IMetricOmmPoolActions` and `MetricOmmPool`, reverting if the computed amounts fall below the caller's floor.
2. Alternatively, create a periphery `MetricOmmPoolLiquidityRemover` contract (analogous to `MetricOmmPoolLiquidityAdder`) that wraps the pool call and enforces minimum-out checks, plus an optional deadline.

---

### Proof of Concept

```
Setup:
  Bin 0 holds: token0BalanceScaled = 1_000_000, token1BalanceScaled = 1_000_000
  binTotalShares[0] = 2_000_000
  Alice owns 1_000_000 shares in bin 0 (50%)

Alice submits removeLiquidity(deltas={binIdxs:[0], shares:[1_000_000]})
  Expected: amount0Removed = 500_000 token0, amount1Removed = 500_000 token1

Attacker front-runs with swap (zeroForOne=false, exact-out token0):
  Drains all token0 from bin 0 → token0BalanceScaled = 0, token1BalanceScaled ≈ 2_000_000

Alice's removeLiquidity executes:
  amount0Scaled = 0 * 1_000_000 / 2_000_000 = 0
  amount1Scaled = 2_000_000 * 1_000_000 / 2_000_000 = 1_000_000

Alice receives: 0 token0, 1_000_000 token1
  If token0 price > token1 price, Alice has lost value with no recourse.
```

### Citations

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L205-206)
```text
          uint256 amount0Scaled = _checkedMul(binState.token0BalanceScaled, sharesToRemove) / binTotalSharesVal;
          uint256 amount1Scaled = _checkedMul(binState.token1BalanceScaled, sharesToRemove) / binTotalSharesVal;
```

**File:** metric-core/contracts/MetricOmmPool.sol (L206-206)
```text
    if (msg.sender != owner) revert NotPositionOwner();
```

**File:** metric-core/contracts/MetricOmmPool.sol (L208-211)
```text
    (amount0Removed, amount1Removed) = LiquidityLib.removeLiquidity(
      _liquidityContext(), owner, salt, deltas, binTotals, _binStates, _binTotalShares, _positionBinShares
    );
    _afterRemoveLiquidity(msg.sender, owner, salt, deltas, amount0Removed, amount1Removed, extensionData);
```

**File:** metric-core/contracts/MetricOmmPool.sol (L735-739)
```text
        binTotals.scaledToken0 =
          (uint256(binTotals.scaledToken0) + uint256(amount0DeltaScaled) - protocolFeeScaled).toUint128(); // forge-lint: disable-line(unsafe-typecast)
        // casting to uint128/uint256 is safe because bin totals remain bounded by uint128-scaled accounting invariants.
        // forge-lint: disable-next-line(unsafe-typecast)
        binTotals.scaledToken1 = uint128(uint256(binTotals.scaledToken1) - uint256(-amount1DeltaScaled));
```

**File:** metric-core/contracts/libraries/SwapMath.sol (L639-641)
```text
      binState.token0BalanceScaled -= out0Scaled.toUint104();
      binState.token1BalanceScaled =
        uint256((binState.token1BalanceScaled) + totalIn1Scaled - protocolFeeAmountScaled).toUint104();
```

**File:** metric-core/contracts/interfaces/IMetricOmmPool/IMetricOmmPoolActions.sol (L172-174)
```text
  function removeLiquidity(address owner, uint80 salt, LiquidityDelta calldata deltas, bytes calldata extensionData)
    external
    returns (uint256 amount0Removed, uint256 amount1Removed);
```

**File:** metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol (L165-167)
```text
    if (amount0Delta > max0 || amount1Delta > max1) {
      revert MaxAmountExceeded(amount0Delta, amount1Delta, max0, max1);
    }
```
