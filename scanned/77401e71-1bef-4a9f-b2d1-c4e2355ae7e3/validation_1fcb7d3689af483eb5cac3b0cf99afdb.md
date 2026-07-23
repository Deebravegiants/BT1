### Title
`addLiquidityWeighted` Reverts with `MinimalLiquidity` When Scaled Shares Fall Below Pool Floor — (`metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol`)

### Summary

`MetricOmmPoolLiquidityAdder.addLiquidityWeighted` uses a probe-then-scale pattern. After the probe determines `need0`/`need1`, `_scaleWeightsToShares` multiplies each weight by `min(max0/need0, max1/need1)`. The only guard on the scaled result is `SharesRoundedToZero` (catches `== 0`). When the scale factor is small but non-zero, scaled shares can land in the range `[1, MINIMAL_MINTABLE_LIQUIDITY − 1]`, causing the subsequent `addLiquidity` call to revert with `MinimalLiquidity`. There is no way for the caller to recover from this without abandoning the weighted path entirely.

### Finding Description

`_scaleWeightsToShares` computes:

```solidity
out.shares[i] = Math.mulDiv(w.shares[i], scaleWad, WAD);
if (w.shares[i] != 0 && out.shares[i] == 0) revert SharesRoundedToZero();
``` [1](#0-0) 

The guard only rejects the zero case. Any value in `[1, MINIMAL_MINTABLE_LIQUIDITY − 1]` passes silently. The scaled `LiquidityDelta` is then forwarded to `LiquidityLib.addLiquidity`, which enforces:

```solidity
uint256 newUserShares = userShares + sharesToAdd;
if (newUserShares < ctx.minimalMintableLiquidity) {
    revert IMetricOmmPoolActions.MinimalLiquidity(newUserShares, ctx.minimalMintableLiquidity);
}
``` [2](#0-1) 

`MINIMAL_MINTABLE_LIQUIDITY` is an immutable set at pool construction time. [3](#0-2) 

The probe step already committed state changes inside the pool (they are reverted by the `LiquidityProbe` revert), but the second paying call reverts at the pool level after the `_setPayContext` transient write, leaving the caller with no tokens moved but a permanently broken call path for that `(max0, max1)` combination.

### Impact Explanation

Any caller of `addLiquidityWeighted` whose `maxAmountToken0`/`maxAmountToken1` caps produce a scale factor that maps weight shares into `[1, MINIMAL_MINTABLE_LIQUIDITY − 1]` will receive an opaque `MinimalLiquidity` revert. The weighted liquidity path — the primary ergonomic entry point for LPs who specify token budgets rather than raw shares — is broken for this cap range. No funds are lost, but the core periphery liquidity flow is unusable without switching to `addLiquidityExactShares` and computing shares manually.

### Likelihood Explanation

The condition is reachable by any unprivileged LP. It occurs whenever `max0` (or `max1`) is small relative to `need0` (or `need1`) but not so small that shares round to zero. For example, with `MINIMAL_MINTABLE_LIQUIDITY = 1000` and weight shares of `5_000_000`, a cap that produces `scaleWad ≈ 0.0002e18` yields `out.shares ≈ 1000`; a cap slightly below that yields `out.shares = 999`, which reverts. This is a normal operating range for users trying to deposit small amounts into a pool with large existing liquidity.

### Recommendation

In `_scaleWeightsToShares`, after computing `out.shares[i]`, also check that the result is either zero or at least `MINIMAL_MINTABLE_LIQUIDITY`. Read `MINIMAL_MINTABLE_LIQUIDITY` from the pool immutables (available via `IMetricOmmPool(pool).getImmutables()`) and revert with a descriptive error (e.g., `SharesBelowMinimalLiquidity`) before the paying `addLiquidity` call is attempted. This mirrors the fix applied in the referenced external report: make an explicit exemption/guard for the sub-minimum case rather than letting the inner function revert with a confusing error.

### Proof of Concept

1. Deploy a pool with `MINIMAL_MINTABLE_LIQUIDITY = 1000`.
2. Seed the pool so that a probe with weight `[bin=4, shares=5_000_000]` returns `need0 = 500_000` (1 token0 per 1 share at scale).
3. Call `addLiquidityWeighted` with `maxAmountToken0 = 99` (so `scaleWad = mulDiv(99, 1e18, 500_000) ≈ 198e12`).
4. `_scaleWeightsToShares` computes `out.shares[0] = mulDiv(5_000_000, 198e12, 1e18) = 990`.
5. `990 != 0` → `SharesRoundedToZero` does not fire.
6. The paying `addLiquidity` call reaches `LiquidityLib` and reverts: `MinimalLiquidity(990, 1000)`.
7. The caller receives no tokens moved and no actionable error from the periphery layer. [4](#0-3) [2](#0-1)

### Citations

**File:** metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol (L226-243)
```text
  function _scaleWeightsToShares(LiquidityDelta calldata w, uint256 max0, uint256 max1, uint256 need0, uint256 need1)
    internal
    pure
    returns (LiquidityDelta memory out)
  {
    uint256 scaleWad0 = need0 == 0 ? type(uint256).max : Math.mulDiv(max0, WAD, need0);
    uint256 scaleWad1 = need1 == 0 ? type(uint256).max : Math.mulDiv(max1, WAD, need1);
    uint256 scaleWad = scaleWad0 < scaleWad1 ? scaleWad0 : scaleWad1;

    uint256 n = w.binIdxs.length;
    out.binIdxs = new int256[](n);
    out.shares = new uint256[](n);
    for (uint256 i; i < n; i++) {
      out.binIdxs[i] = w.binIdxs[i];
      out.shares[i] = Math.mulDiv(w.shares[i], scaleWad, WAD);
      if (w.shares[i] != 0 && out.shares[i] == 0) revert SharesRoundedToZero();
    }
  }
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L76-79)
```text
          uint256 newUserShares = userShares + sharesToAdd;
          if (newUserShares < ctx.minimalMintableLiquidity) {
            revert IMetricOmmPoolActions.MinimalLiquidity(newUserShares, ctx.minimalMintableLiquidity);
          }
```

**File:** metric-core/contracts/MetricOmmPool.sol (L55-55)
```text
  uint256 internal immutable MINIMAL_MINTABLE_LIQUIDITY;
```
