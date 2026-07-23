### Title
Precision Loss in `removeLiquidity` Burns LP Shares Without Returning Tokens — (File: `metric-core/contracts/libraries/LiquidityLib.sol`)

---

### Summary

In `LiquidityLib.removeLiquidity`, the floor division used to compute token amounts owed to an LP rounds down to zero when `sharesToRemove` is small relative to `binTotalSharesVal`. The user's shares are burned and `binTotalShares` is decremented, but the bin's token balances are unchanged and the user receives nothing. This is the direct analog of the Cooler `repay` precision bug: one accounting dimension (shares) decreases while the other (bin token balances) does not, causing a silent loss of principal.

---

### Finding Description

In `LiquidityLib.removeLiquidity`:

```solidity
uint256 amount0Scaled = _checkedMul(binState.token0BalanceScaled, sharesToRemove) / binTotalSharesVal;
uint256 amount1Scaled = _checkedMul(binState.token1BalanceScaled, sharesToRemove) / binTotalSharesVal;
``` [1](#0-0) 

Both use plain floor division. When `binState.token0BalanceScaled * sharesToRemove < binTotalSharesVal`, `amount0Scaled` rounds to zero (and likewise for token1). The code then:

1. Subtracts `0` from `binState.token0BalanceScaled` and `binState.token1BalanceScaled` — bin balances **unchanged**.
2. Decrements `binTotalShares[binIdx]` by `sharesToRemove` — total shares **decrease**.
3. Decrements `positionBinShares[posKey]` by `sharesToRemove` — user's shares **decrease**.
4. Transfers `0` tokens to the user. [2](#0-1) 

The only guard present is:

```solidity
if (newUserShares > 0 && newUserShares < ctx.minimalMintableLiquidity) {
    revert IMetricOmmPoolActions.MinimalLiquidity(newUserShares, ctx.minimalMintableLiquidity);
}
``` [3](#0-2) 

This guard only prevents the **remaining** shares from falling below the minimum; it does not prevent removing a small number of shares that yields zero tokens. A full removal (`newUserShares == 0`) also bypasses it because `0 > 0` is false.

The asymmetry is structural: `addLiquidity` uses `Math.ceilDiv` (rounds up, user always pays ≥ 1 scaled unit), while `removeLiquidity` uses floor division (user may receive 0). [4](#0-3) 

---

### Impact Explanation

**Direct loss of LP principal.** The user burns real shares and receives zero tokens. The value of the burned shares is silently redistributed to remaining LPs in the same bin (their per-share entitlement increases because the same bin balance is now divided among fewer shares). This is a loss of user funds above the Sherlock Medium threshold whenever the burned shares have non-trivial value.

The `binTotals` accounting remains internally consistent (since `totalToken0ToRemoveScaled == 0` means `binTotals.scaledToken0` is not decremented either), so the pool does not become insolvent — but the individual LP's claim is permanently destroyed. [5](#0-4) 

---

### Likelihood Explanation

No privileged access is required. Any LP can trigger this on their own position by calling `removeLiquidity` with a `sharesToRemove` value small enough that:

```
binState.token0BalanceScaled * sharesToRemove < binTotalSharesVal
binState.token1BalanceScaled * sharesToRemove < binTotalSharesVal
```

This condition is more likely when:
- A bin's token balances have been reduced by swaps (low `token0BalanceScaled` / `token1BalanceScaled`).
- The total share count is large relative to the user's position.
- Token decimals differ greatly (amplifying the scaled-unit gap), since `TOKEN_X_SCALE_MULTIPLIER` can be up to `10^18`. [6](#0-5) 

---

### Recommendation

Revert if both computed amounts are zero while the bin holds non-zero balances and the user is removing non-zero shares:

```solidity
if (
    sharesToRemove > 0 &&
    amount0Scaled == 0 &&
    amount1Scaled == 0 &&
    (binState.token0BalanceScaled > 0 || binState.token1BalanceScaled > 0)
) {
    revert ZeroTokensReturned();
}
```

This mirrors the Cooler recommendation: prevent the operation when the returned collateral (here: tokens) would be zero.

---

### Proof of Concept

**Setup:**
- Bin state: `token0BalanceScaled = 100`, `token1BalanceScaled = 100`, `binTotalShares = 10 000`
- User holds 50 shares (0.5 % of total)

**Attack / accidental trigger:**
1. User calls `removeLiquidity` with `sharesToRemove = 1`.
2. `amount0Scaled = (100 × 1) / 10 000 = 0` (floor division).
3. `amount1Scaled = (100 × 1) / 10 000 = 0` (floor division).
4. `binState.token0BalanceScaled` stays at 100; `binState.token1BalanceScaled` stays at 100.
5. `binTotalShares` decreases from 10 000 to 9 999.
6. `positionBinShares` decreases from 50 to 49.
7. User receives **0 tokens** despite burning a real share.
8. Remaining 9 999 shares now represent 100 token0 and 100 token1 — each share is worth slightly more, at the burned user's expense.

Repeating this iteratively (or with a larger `sharesToRemove` that still satisfies the rounding condition) drains the user's entire position without any token return.

### Citations

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L109-110)
```text
            amount0Scaled = Math.ceilDiv(_checkedMul(binState.token0BalanceScaled, sharesToAdd), binTotalSharesVal);
            amount1Scaled = Math.ceilDiv(_checkedMul(binState.token1BalanceScaled, sharesToAdd), binTotalSharesVal);
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L200-202)
```text
          if (newUserShares > 0 && newUserShares < ctx.minimalMintableLiquidity) {
            revert IMetricOmmPoolActions.MinimalLiquidity(newUserShares, ctx.minimalMintableLiquidity);
          }
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L205-206)
```text
          uint256 amount0Scaled = _checkedMul(binState.token0BalanceScaled, sharesToRemove) / binTotalSharesVal;
          uint256 amount1Scaled = _checkedMul(binState.token1BalanceScaled, sharesToRemove) / binTotalSharesVal;
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L209-217)
```text
          // forge-lint: disable-next-line(unsafe-typecast)
          binState.token0BalanceScaled -= uint104(amount0Scaled);
          // forge-lint: disable-next-line(unsafe-typecast)
          binState.token1BalanceScaled -= uint104(amount1Scaled);
          binTotalShares[binIdx] = binTotalSharesVal - sharesToRemove;
          positionBinShares[posKey] = newUserShares;

          totalToken0ToRemoveScaled += amount0Scaled;
          totalToken1ToRemoveScaled += amount1Scaled;
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L230-237)
```text
      if (totalToken0ToRemoveScaled > 0) {
        // forge-lint: disable-next-line(unsafe-typecast)
        binTotals.scaledToken0 = uint128(uint256(binTotals.scaledToken0) - totalToken0ToRemoveScaled);
      }
      if (totalToken1ToRemoveScaled > 0) {
        // forge-lint: disable-next-line(unsafe-typecast)
        binTotals.scaledToken1 = uint128(uint256(binTotals.scaledToken1) - totalToken1ToRemoveScaled);
      }
```

**File:** metric-core/contracts/MetricOmmPool.sol (L48-51)
```text
  /// @notice Multiplier to scale token0 external amounts to internal: 10^(max(18, decimals) - token0.decimals())
  uint256 internal immutable TOKEN_0_SCALE_MULTIPLIER;
  /// @notice Multiplier to scale token1 external amounts to internal: 10^(max(18, decimals) - token1.decimals())
  uint256 internal immutable TOKEN_1_SCALE_MULTIPLIER;
```
