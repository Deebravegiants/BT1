The code confirms all three cited locations exactly as described. Let me verify the critical logic:

Audit Report

## Title
`addLiquidityWeighted` Reverts with `MinimalLiquidity` When Scaled Shares Fall Below Pool Floor — (`metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol`)

## Summary

`_scaleWeightsToShares` only guards against shares scaling to exactly zero (`SharesRoundedToZero`), but does not guard against scaled shares landing in `[1, MINIMAL_MINTABLE_LIQUIDITY − 1]`. When this occurs, the subsequent paying `addLiquidity` call reaches `LiquidityLib.addLiquidity` and reverts with `MinimalLiquidity`, making `addLiquidityWeighted` — the primary ergonomic LP entry point — permanently unusable for that `(max0, max1)` combination without switching to `addLiquidityExactShares`.

## Finding Description

In `_scaleWeightsToShares` (L226–243 of `MetricOmmPoolLiquidityAdder.sol`), the scale factor is computed as `min(max0/need0, max1/need1)` in WAD precision, then applied to each weight share:

```solidity
out.shares[i] = Math.mulDiv(w.shares[i], scaleWad, WAD);
if (w.shares[i] != 0 && out.shares[i] == 0) revert SharesRoundedToZero();
```

The only guard is the zero check. Any result in `[1, MINIMAL_MINTABLE_LIQUIDITY − 1]` passes silently. The scaled `LiquidityDelta` is then forwarded through `_addLiquidity` → `IMetricOmmPoolActions(pool).addLiquidity(...)` → `LiquidityLib.addLiquidity`, which enforces at L76–79:

```solidity
uint256 newUserShares = userShares + sharesToAdd;
if (newUserShares < ctx.minimalMintableLiquidity) {
    revert IMetricOmmPoolActions.MinimalLiquidity(newUserShares, ctx.minimalMintableLiquidity);
}
```

For a fresh position (`userShares == 0`), `newUserShares == sharesToAdd`. If `sharesToAdd` is in `[1, MINIMAL_MINTABLE_LIQUIDITY − 1]`, the revert fires. `MINIMAL_MINTABLE_LIQUIDITY` is an immutable set at pool construction time (L55 of `MetricOmmPool.sol`) and is accessible via `IMetricOmmPool(pool).getImmutables()` — but `_scaleWeightsToShares` never reads it. No `SharesBelowMinimal` or equivalent guard exists anywhere in the periphery codebase.

The probe step reverts cleanly (pool state unchanged), but the paying call reverts at the pool level after `_setPayContext` writes transient storage. The catch block in `_addLiquidity` re-bubbles the `MinimalLiquidity` error to the caller with no actionable periphery-level context.

## Impact Explanation

The `addLiquidityWeighted` function — the primary ergonomic entry point for LPs specifying token budgets — is broken for any `(max0, max1)` combination that produces a scale factor mapping weight shares into `[1, MINIMAL_MINTABLE_LIQUIDITY − 1]` for a fresh position. This constitutes broken core pool liquidity functionality. No funds are lost, but the LP cannot add liquidity via the weighted path for this cap range without manually computing shares and switching to `addLiquidityExactShares`.

## Likelihood Explanation

The condition is reachable by any unprivileged LP with no special setup. It occurs whenever the user's token caps are small relative to the probe's `need0`/`need1` but not so small that shares round to zero. With `MINIMAL_MINTABLE_LIQUIDITY = 1000` and weight shares of `5_000_000`, a `maxAmountToken0` that produces `scaleWad ≈ 0.0002e18` yields `out.shares ≈ 1000`; a cap slightly below that yields `out.shares = 999`, which reverts. This is a normal operating range for users depositing small amounts into a pool with large existing liquidity, and is repeatable for any caller.

## Recommendation

In `_scaleWeightsToShares`, after computing `out.shares[i]`, add a check that the result is either zero or at least `MINIMAL_MINTABLE_LIQUIDITY`. Read the value from `IMetricOmmPool(pool).getImmutables()` (the callback already calls `getImmutables()` at L169) and revert with a descriptive error (e.g., `SharesBelowMinimalLiquidity(out.shares[i], minimalMintableLiquidity)`) before the paying `addLiquidity` call is attempted. This surfaces the failure at the periphery layer with an actionable error rather than letting the inner pool revert with an opaque `MinimalLiquidity`.

## Proof of Concept

1. Deploy a pool with `MINIMAL_MINTABLE_LIQUIDITY = 1000`.
2. Seed the pool so a probe with `weightDeltas = [{binIdx: 4, shares: 5_000_000}]` returns `need0 = 500_000`, `need1 = 0`.
3. Call `addLiquidityWeighted` with `maxAmountToken0 = 99`, `maxAmountToken1 = type(uint256).max`.
4. `_scaleWeightsToShares` computes `scaleWad = mulDiv(99, 1e18, 500_000) = 198_000_000_000_000` (~`198e12`).
5. `out.shares[0] = mulDiv(5_000_000, 198e12, 1e18) = 990`.
6. `990 != 0` → `SharesRoundedToZero` does not fire; scaled delta `[{binIdx: 4, shares: 990}]` is forwarded.
7. `LiquidityLib.addLiquidity` evaluates `newUserShares = 0 + 990 = 990 < 1000` and reverts: `MinimalLiquidity(990, 1000)`.
8. `_addLiquidity` catch block re-bubbles the error; caller receives `MinimalLiquidity` with no periphery context and no path to recover via `addLiquidityWeighted` for this cap. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol (L238-242)
```text
    for (uint256 i; i < n; i++) {
      out.binIdxs[i] = w.binIdxs[i];
      out.shares[i] = Math.mulDiv(w.shares[i], scaleWad, WAD);
      if (w.shares[i] != 0 && out.shares[i] == 0) revert SharesRoundedToZero();
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
