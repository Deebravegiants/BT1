The overflow claim is real but gated by `_checkedMul`. Let me trace the exact conditions.

### Title
`LiquidityLib.addLiquidity` unchecked `binTotalShares` overflow corrupts bin share accounting, permanently breaking `removeLiquidity` and enabling future-LP fund theft — (`metric-core/contracts/libraries/LiquidityLib.sol`)

---

### Summary

The entire body of `LiquidityLib.addLiquidity` runs inside a single `unchecked { }` block. The write `binTotalShares[binIdx] = binTotalSharesVal + sharesToAdd` at line 120 can silently wrap to zero when `sharesToAdd = type(uint256).max - binTotalSharesVal + 1`. The only arithmetic guard that could block this — `_checkedMul` — is an `internal pure` function whose body is **not** inside an `unchecked` block, so it retains Solidity 0.8 overflow protection. However, `_checkedMul(0, sharesToAdd)` returns 0 without reverting, meaning the guard is bypassed whenever both `token0BalanceScaled` and `token1BalanceScaled` of the target bin are zero — a state that arises naturally after a bin is fully consumed by swaps.

---

### Finding Description

**Relevant code:**

`LiquidityLib.addLiquidity` wraps its entire loop in `unchecked`: [1](#0-0) 

Inside that loop, the only overflow-sensitive multiplications are delegated to `_checkedMul`: [2](#0-1) 

`_checkedMul` is: [3](#0-2) 

Because Solidity 0.8's `unchecked` does **not** propagate into called functions, `_checkedMul` retains overflow checking — but only when `a > 0`. When `a == 0`, `0 * b == 0` regardless of `b`, so no overflow fires.

The unchecked write that corrupts state: [4](#0-3) 

The minimum-liquidity guard only checks a lower bound, not an upper bound, so a wrapped `newUserShares` that is a very large number passes silently: [5](#0-4) 

**Precondition — empty bin with non-zero shares:**

Swaps update `token0BalanceScaled` / `token1BalanceScaled` directly (e.g. `binState.token1BalanceScaled -= out1Scaled.toUint104()`) but never touch `binTotalShares`. A bin below the current price holds only token1; after a swap fully consumes it, both balances are 0 while `binTotalShares[binIdx]` remains the original LP's share count. This is a normal, reachable state confirmed by the swap loop logic: [6](#0-5) 

**Attack steps:**

1. LP adds liquidity to bin `B` (e.g. bin −1, below current price). `binTotalShares[B] = S`, `token1BalanceScaled = T > 0`, `token0BalanceScaled = 0`.
2. Normal swap activity fully drains bin `B`: `token1BalanceScaled → 0`. Now `binTotalShares[B] = S`, both balances = 0.
3. Attacker calls `addLiquidity` with `sharesToAdd = type(uint256).max - S + 1` for bin `B`.
   - `_checkedMul(0, sharesToAdd) = 0` for both legs — no revert.
   - `amount0Scaled = amount1Scaled = 0` — attacker pays **nothing**.
   - `binTotalShares[B] = S + (type(uint256).max - S + 1) = 0` (wraps).
   - `positionBinShares[attackerKey] = type(uint256).max - S + 1` (huge).
4. Any subsequent `removeLiquidity` call for bin `B` executes: [7](#0-6) 
   `binTotalSharesVal = 0` → division-by-zero → permanent revert for all users of that bin.

**Secondary fund-loss path (future LP):**

After the corruption, if a new LP adds liquidity to bin `B`:
- `binTotalSharesVal == 0` triggers the initial-rate branch (line 85), so the new LP pays tokens and `binTotalShares[B]` becomes `newShares`.
- The original LP (whose `positionBinShares` was never cleared) calls `removeLiquidity` with their original `S` shares. `amount0Scaled = newLP_balance * S / newShares`. If `S > newShares`, the original LP withdraws more than the new LP deposited, draining the new LP's principal. The subsequent `binState.token0BalanceScaled -= uint104(amount0Scaled)` underflows (unchecked), further corrupting global `binTotals`. [8](#0-7) 

---

### Impact Explanation

- **Broken core functionality:** `removeLiquidity` permanently reverts (division-by-zero) for all positions in the affected bin.
- **Fund loss for future LPs:** Any LP who adds liquidity to the corrupted bin can have their deposit drained by a holder of stale `positionBinShares`, with the pool's `binTotals` corrupted by the resulting underflow.

---

### Likelihood Explanation

- Bins being fully consumed by swaps is a routine, expected event in any active pool.
- The attack costs the attacker zero tokens (both `amount0Scaled` and `amount1Scaled` are 0 when the bin is empty).
- The attacker only needs to know the current `binTotalShares[B]` value (readable via `PoolStateLibrary` / `EXTSLOAD`) to compute the exact `sharesToAdd`.
- No privileged role is required; `addLiquidity` is a public entry point.

---

### Recommendation

Remove the blanket `unchecked { }` wrapper from `addLiquidity`, or add an explicit upper-bound check before the write:

```solidity
// Before: binTotalShares[binIdx] = binTotalSharesVal + sharesToAdd;
uint256 newBinTotal = binTotalSharesVal + sharesToAdd;
if (newBinTotal < binTotalSharesVal) revert SharesOverflow();
binTotalShares[binIdx] = newBinTotal;
```

Apply the same guard to `newUserShares = userShares + sharesToAdd` (line 76). Alternatively, move the `binTotalShares` and `positionBinShares` writes outside the `unchecked` block so Solidity's default overflow protection applies.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.35;

import "forge-std/Test.sol";
// ... pool setup imports ...

contract BinTotalSharesOverflowTest is Test {
    // Setup: deploy pool with bins [-1, 0, 1], add LP to bin -1 (token1 only)
    // Then drain bin -1 via swap (token0 -> token1 direction)

    function test_binTotalSharesOverflow() public {
        // 1. LP adds liquidity to bin -1
        uint256 lpShares = 1_000_000e18;
        _addLiquidity(lp, -1, lpShares);

        // 2. Drain bin -1 via swap (buy token1, sell token0)
        _drainBin(-1); // swap until token1BalanceScaled == 0

        // Verify precondition: both balances 0, shares non-zero
        (uint104 t0, uint104 t1,,,) = pool.getBinState(-1);
        assertEq(t0, 0);
        assertEq(t1, 0);
        uint256 totalShares = pool.binTotalShares(-1);
        assertGt(totalShares, 0);

        // 3. Attacker calls addLiquidity with overflow sharesToAdd
        uint256 overflowShares = type(uint256).max - totalShares + 1;
        _addLiquidity(attacker, -1, overflowShares); // pays 0 tokens

        // 4. binTotalShares is now 0
        assertEq(pool.binTotalShares(-1), 0);

        // 5. LP's removeLiquidity reverts with division-by-zero
        vm.expectRevert(); // Panic: division by zero
        _removeLiquidity(lp, -1, lpShares);
    }
}
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

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L205-206)
```text
          uint256 amount0Scaled = _checkedMul(binState.token0BalanceScaled, sharesToRemove) / binTotalSharesVal;
          uint256 amount1Scaled = _checkedMul(binState.token1BalanceScaled, sharesToRemove) / binTotalSharesVal;
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L210-213)
```text
          binState.token0BalanceScaled -= uint104(amount0Scaled);
          // forge-lint: disable-next-line(unsafe-typecast)
          binState.token1BalanceScaled -= uint104(amount1Scaled);
          binTotalShares[binIdx] = binTotalSharesVal - sharesToRemove;
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L261-263)
```text
  function _checkedMul(uint256 a, uint256 b) internal pure returns (uint256) {
    return a * b;
  }
```

**File:** metric-core/contracts/MetricOmmPool.sol (L1154-1163)
```text
      while (state.amountSpecifiedRemainingScaled > 0) {
        bool nonEmptyBin = true;
        if (binState.token1BalanceScaled == 0 || curPosInBinCache == 0) {
          if (params.priceLimitX64 != 0 && params.priceLimitX64 >= lowerPriceX64) {
            break;
          }
          if (totalAvailableToken1Scaled == 0) {
            break;
          }
          nonEmptyBin = false;
```
