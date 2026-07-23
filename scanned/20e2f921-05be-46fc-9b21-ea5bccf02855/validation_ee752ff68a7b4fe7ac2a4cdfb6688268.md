### Title
Free LP Share Minting When Bin Token Balances Are Zero — (`metric-core/contracts/libraries/LiquidityLib.sol`)

---

### Summary

When a bin's token balances are fully drained to zero by a swap (while `binTotalShares` remains non-zero), `LiquidityLib.addLiquidity` allows any caller to mint an arbitrary number of shares for **zero tokens**. These free shares dilute existing LP claims on all future tokens that enter the bin, causing a direct loss of LP principal.

---

### Finding Description

In `LiquidityLib.addLiquidity`, when `binTotalSharesVal != 0`, the token cost for new shares is computed proportionally:

```solidity
// LiquidityLib.sol lines 109-110
amount0Scaled = Math.ceilDiv(_checkedMul(binState.token0BalanceScaled, sharesToAdd), binTotalSharesVal);
amount1Scaled = Math.ceilDiv(_checkedMul(binState.token1BalanceScaled, sharesToAdd), binTotalSharesVal);
``` [1](#0-0) 

If `token0BalanceScaled == 0` **and** `token1BalanceScaled == 0` (both bin balances drained to zero by a swap), then `amount0Scaled = 0` and `amount1Scaled = 0` regardless of `sharesToAdd`. The code then skips the callback entirely:

```solidity
// lines 144-154
if (amount0Added > 0 || amount1Added > 0) {
  // callback NOT triggered — no tokens pulled from caller
}
``` [2](#0-1) 

But shares **are** unconditionally credited:

```solidity
// lines 120-121
binTotalShares[binIdx] = binTotalSharesVal + sharesToAdd;
positionBinShares[posKey] = newUserShares;
``` [3](#0-2) 

Swaps do drain bin balances to zero when a bin is fully traversed (e.g., `token0BalanceScaled` decremented to 0 in `SwapMath`), but `_binTotalShares` is never modified by the swap path — it is only touched by `addLiquidity`/`removeLiquidity`. [4](#0-3) 

The `minimalMintableLiquidity` guard only enforces a floor on `newUserShares`, not a minimum token payment:

```solidity
// line 77-79
if (newUserShares < ctx.minimalMintableLiquidity) {
  revert IMetricOmmPoolActions.MinimalLiquidity(newUserShares, ctx.minimalMintableLiquidity);
}
``` [5](#0-4) 

Once the attacker holds free shares, `removeLiquidity` uses **floor division**:

```solidity
// lines 205-206
uint256 amount0Scaled = _checkedMul(binState.token0BalanceScaled, sharesToRemove) / binTotalSharesVal;
uint256 amount1Scaled = _checkedMul(binState.token1BalanceScaled, sharesToRemove) / binTotalSharesVal;
``` [6](#0-5) 

When the bin later receives tokens (from a reverse swap), the attacker's free shares entitle them to a proportional cut of those tokens, directly reducing what honest LPs receive.

---

### Impact Explanation

Existing LPs who deposited tokens into a bin suffer a direct loss of their proportional claim. After the attacker mints `N` free shares into a bin with `V` existing shares, honest LPs collectively own only `V / (V + N)` of future bin receipts instead of 100%. The attacker can make `N` arbitrarily large (bounded only by `uint256`), approaching a 100% dilution of existing LP claims. This is a direct loss of owed LP assets.

---

### Likelihood Explanation

A bin reaches `token0BalanceScaled == 0 && token1BalanceScaled == 0` whenever a swap fully traverses it — a normal operational event in any active pool. The attacker does not need to be the first depositor, does not need to front-run, and does not need to pay any swap fees themselves: they only need to observe the drained state (on-chain readable via `EXTSLOAD`/`PoolStateLibrary`) and call `addLiquidity` before the bin refills. The only cost is gas and the `minimalMintableLiquidity` floor, which is a pool-creation parameter and can be set to a small value.

---

### Recommendation

In the `binTotalSharesVal != 0` branch of `addLiquidity`, treat a fully-drained bin (both balances zero) the same as `binTotalSharesVal == 0` — i.e., fall back to the `initialScaledToken*PerShareE18` rate for pricing new shares. Alternatively, revert if both balances are zero and `binTotalSharesVal > 0`, forcing the bin to be re-initialized only after all existing shares are burned.

```solidity
} else {
  // Guard: if bin is fully drained, treat as fresh (or revert)
  if (binState.token0BalanceScaled == 0 && binState.token1BalanceScaled == 0) {
    revert BinFullyDrained(); // or fall back to initialScaledToken*PerShareE18 path
  }
  amount0Scaled = Math.ceilDiv(...);
  amount1Scaled = Math.ceilDiv(...);
}
```

---

### Proof of Concept

**Setup:** Pool with token0/token1, bin index `+1` (above current price, holds only token0). `minimalMintableLiquidity = 1000`. `initialScaledToken0PerShareE18 = 1e18`.

1. **Victim LP** calls `addLiquidity` for bin `+1` with `shares = 100_000`.
   - Pays `100_000` scaled token0.
   - State: `binTotalShares[1] = 100_000`, `token0BalanceScaled = 100_000`.

2. **Swap** (zeroForOne, exact output) fully traverses bin `+1`, consuming all `100_000` scaled token0.
   - State: `binTotalShares[1] = 100_000` (unchanged), `token0BalanceScaled = 0`.

3. **Attacker** calls `addLiquidity` for bin `+1` with `shares = 10_000_000` (100× existing).
   - `binTotalSharesVal = 100_000 != 0` → proportional branch.
   - `amount0Scaled = ceilDiv(0 * 10_000_000, 100_000) = 0`.
   - `amount1Scaled = ceilDiv(0 * 10_000_000, 100_000) = 0`.
   - Callback skipped. Attacker pays **0 tokens**.
   - State: `binTotalShares[1] = 10_100_000`, attacker holds `10_000_000` shares.

4. **Reverse swap** refills bin `+1` with `50_000` scaled token0.
   - State: `token0BalanceScaled = 50_000`.

5. **Attacker** calls `removeLiquidity` for `10_000_000` shares.
   - `amount0Scaled = 50_000 * 10_000_000 / 10_100_000 ≈ 49_505` scaled token0.
   - Attacker receives ~49,505 scaled token0 having paid **zero**.

6. **Victim LP** calls `removeLiquidity` for `100_000` shares.
   - `amount0Scaled = 495 * 100_000 / 100_000 = 495` scaled token0.
   - Victim receives only ~495 out of the 50,000 that entered the bin — a ~99% loss of their proportional claim.

### Citations

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L77-79)
```text
          if (newUserShares < ctx.minimalMintableLiquidity) {
            revert IMetricOmmPoolActions.MinimalLiquidity(newUserShares, ctx.minimalMintableLiquidity);
          }
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L108-111)
```text
          } else {
            amount0Scaled = Math.ceilDiv(_checkedMul(binState.token0BalanceScaled, sharesToAdd), binTotalSharesVal);
            amount1Scaled = Math.ceilDiv(_checkedMul(binState.token1BalanceScaled, sharesToAdd), binTotalSharesVal);
          }
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L120-121)
```text
          binTotalShares[binIdx] = binTotalSharesVal + sharesToAdd;
          positionBinShares[posKey] = newUserShares;
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L144-155)
```text
      if (amount0Added > 0 || amount1Added > 0) {
        uint256 balance0Before = IERC20(ctx.token0).balanceOf(address(this));
        uint256 balance1Before = IERC20(ctx.token1).balanceOf(address(this));
        IMetricOmmModifyLiquidityCallback(msg.sender)
          .metricOmmModifyLiquidityCallback(amount0Added, amount1Added, callbackData);
        if (amount0Added > 0 && balance0Before + amount0Added > IERC20(ctx.token0).balanceOf(address(this))) {
          revert IMetricOmmPoolActions.InsufficientTokenBalance();
        }
        if (amount1Added > 0 && balance1Before + amount1Added > IERC20(ctx.token1).balanceOf(address(this))) {
          revert IMetricOmmPoolActions.InsufficientTokenBalance();
        }
      }
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L205-206)
```text
          uint256 amount0Scaled = _checkedMul(binState.token0BalanceScaled, sharesToRemove) / binTotalSharesVal;
          uint256 amount1Scaled = _checkedMul(binState.token1BalanceScaled, sharesToRemove) / binTotalSharesVal;
```

**File:** metric-core/contracts/MetricOmmPool.sol (L93-98)
```text
  mapping(int256 => BinState) internal _binStates;

  // ++++++++++ Unused when swapping ++++++++
  mapping(int256 => uint256) internal _binTotalShares;
  /// @dev Per-bin position shares keyed by `_positionBinKey`.
  mapping(bytes32 => uint256) internal _positionBinShares;
```
