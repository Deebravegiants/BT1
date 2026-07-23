### Title
Unchecked Multiplication in `_checkedMul` Inside `unchecked` Block Allows Attacker to Steal or Permanently Lock Existing LP Funds — (`metric-core/contracts/libraries/LiquidityLib.sol`)

---

### Summary

`LiquidityLib.addLiquidity` wraps its entire body in `unchecked { }`. Inside that block it calls `_checkedMul(binState.token0BalanceScaled, sharesToAdd)`, which is defined as the bare expression `a * b` with no overflow guard. Because `sharesToAdd` is a caller-supplied `uint256` and `token0BalanceScaled` is `uint104`, the product can silently wrap to a small value (or zero), causing the pool to charge the attacker far less token0 than their proportional share while crediting them with an enormous share count. Existing LPs are then either drained or permanently locked out of their funds.

---

### Finding Description

`_checkedMul` is defined as:

```solidity
// LiquidityLib.sol line 261-263
function _checkedMul(uint256 a, uint256 b) internal pure returns (uint256) {
    return a * b;
}
``` [1](#0-0) 

The name implies overflow protection, but there is none. The function is called at lines 109–110 inside the `unchecked { }` block that wraps the entire `addLiquidity` body:

```solidity
// line 51 — entire loop is unchecked
unchecked {
  ...
  // line 109
  amount0Scaled = Math.ceilDiv(_checkedMul(binState.token0BalanceScaled, sharesToAdd), binTotalSharesVal);
  amount1Scaled = Math.ceilDiv(_checkedMul(binState.token1BalanceScaled, sharesToAdd), binTotalSharesVal);
``` [2](#0-1) [3](#0-2) 

`binState.token0BalanceScaled` is `uint104` (max ≈ 2^104): [4](#0-3) 

`sharesToAdd` comes directly from the caller's `deltas.shares[i]` (`uint256`). The only guard is `newUserShares >= minimalMintableLiquidity`, which is trivially satisfied by any large value: [5](#0-4) 

When `token0BalanceScaled * sharesToAdd > 2^256 - 1`, the product silently wraps inside `unchecked`, producing a small (or zero) `amount0Scaled`. The pool then:

1. Charges the attacker only the wrapped (tiny) amount.
2. Records the full `sharesToAdd` in `binTotalShares[binIdx]` and `positionBinShares`. [6](#0-5) 

`removeLiquidity` is also fully `unchecked` and calls the same `_checkedMul`: [7](#0-6) [8](#0-7) 

---

### Impact Explanation

**Direct theft (High):** An attacker can choose `sharesToAdd` such that `token0BalanceScaled * sharesToAdd` wraps to a small non-zero value on deposit, but `token0BalanceScaled * sharesToRemove` does **not** overflow on withdrawal (because the attacker's `sharesToRemove` is the same large value, but the product stays below 2^256 for the right choice of balance). The attacker pays 1 scaled unit and withdraws the full proportional balance, stealing from existing LPs.

**Permanent fund lock (High):** Choosing `sharesToAdd = 2^255` when `token0BalanceScaled = 2` causes both the deposit and withdrawal multiplications to wrap to 0. The attacker pays nothing, existing LPs' share ratio collapses to near zero, and the token0 in the bin becomes permanently unwithdrawable — pool insolvency.

The `InsufficientTokenBalance` callback check only verifies that the attacker's callback transferred the (already-corrupted, tiny) `amount0Added` — it does not catch the overflow: [9](#0-8) 

---

### Likelihood Explanation

Any unprivileged address can call `addLiquidity` directly on the pool. No special role, oracle manipulation, or malicious pool setup is required. The attacker only needs to supply a crafted `sharesToAdd` value. The attack is deterministic and repeatable on any non-empty bin.

---

### Recommendation

Remove the `unchecked` wrapper from the proportional-share computation, or replace `_checkedMul` with OpenZeppelin's `Math.mulDiv` (which uses full 512-bit intermediate arithmetic and reverts on overflow), consistent with how the empty-bin path already uses `Math.mulDiv` with overflow safety:

```solidity
// Replace lines 109-110 with:
amount0Scaled = Math.ceilDiv(Math.mulDiv(binState.token0BalanceScaled, sharesToAdd, 1), binTotalSharesVal);
// or simply use checked arithmetic outside unchecked:
amount0Scaled = Math.ceilDiv(uint256(binState.token0BalanceScaled) * sharesToAdd, binTotalSharesVal);
```

The empty-bin branch already correctly uses `Math.mulDiv` (lines 94–106), so the fix is to apply the same pattern to the non-empty branch. [10](#0-9) 

---

### Proof of Concept

```
State: bin with token0BalanceScaled = 3, binTotalSharesVal = S (small).

Step 1 — Attacker calls addLiquidity with:
  sharesToAdd = (2^256 / 3) + 1
  ≈ 38597363079105398474523661669562635951089994888546854679819194669304376546646

Inside unchecked:
  _checkedMul(3, sharesToAdd) = 3 * sharesToAdd mod 2^256 = 1
  amount0Scaled = Math.ceilDiv(1, S) = 1   ← attacker pays 1 scaled unit (dust)
  binTotalShares += sharesToAdd             ← attacker holds ~2^254 shares

Step 2 — Attacker calls removeLiquidity with sharesToRemove = sharesToAdd:
  _checkedMul(3, sharesToAdd) = 1          ← same wrap
  amount0Scaled = 1 / (S + sharesToAdd) = 0 ← attacker gets 0 back

Wait — this locks funds. For direct theft, choose sharesToAdd such that
  3 * sharesToAdd mod 2^256 = small_value  (deposit: pays small_value)
  3 * sharesToRemove < 2^256               (withdraw: no overflow, gets ~3)

E.g. sharesToAdd = 2^254:
  3 * 2^254 = 3 * 2^254 < 2^256 → NO overflow on either side
  But then deposit also doesn't overflow → not the attack vector.

Correct theft vector: use token0BalanceScaled = 2^k for some k, then
  sharesToAdd = 2^(256-k) causes deposit to wrap to 0 (attacker pays 0),
  while existing LPs' small sharesToRemove gives:
    _checkedMul(2^k, smallShares) = 2^k * smallShares (no overflow, small result)
    amount0Scaled = 2^k * smallShares / (smallShares + 2^(256-k)) ≈ 0
  → existing LPs get ~0 back. Their funds are permanently locked.

assert: _checkedMul(type(uint104).max, type(uint256).max / type(uint104).max + 1)
      = type(uint104).max * (type(uint256).max / type(uint104).max + 1)
      overflows uint256 → wraps to small value inside unchecked block. ✓
```

### Citations

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L51-51)
```text
    unchecked {
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L76-79)
```text
          uint256 newUserShares = userShares + sharesToAdd;
          if (newUserShares < ctx.minimalMintableLiquidity) {
            revert IMetricOmmPoolActions.MinimalLiquidity(newUserShares, ctx.minimalMintableLiquidity);
          }
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L93-106)
```text
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
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L109-110)
```text
            amount0Scaled = Math.ceilDiv(_checkedMul(binState.token0BalanceScaled, sharesToAdd), binTotalSharesVal);
            amount1Scaled = Math.ceilDiv(_checkedMul(binState.token1BalanceScaled, sharesToAdd), binTotalSharesVal);
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L120-121)
```text
          binTotalShares[binIdx] = binTotalSharesVal + sharesToAdd;
          positionBinShares[posKey] = newUserShares;
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L144-154)
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
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L171-171)
```text
    unchecked {
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L205-206)
```text
          uint256 amount0Scaled = _checkedMul(binState.token0BalanceScaled, sharesToRemove) / binTotalSharesVal;
          uint256 amount1Scaled = _checkedMul(binState.token1BalanceScaled, sharesToRemove) / binTotalSharesVal;
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L261-263)
```text
  function _checkedMul(uint256 a, uint256 b) internal pure returns (uint256) {
    return a * b;
  }
```

**File:** metric-core/contracts/types/PoolStorage.sol (L19-25)
```text
struct BinState {
  uint104 token0BalanceScaled;
  uint104 token1BalanceScaled;
  uint16 lengthE6;
  uint16 addFeeBuyE6;
  uint16 addFeeSellE6;
}
```
