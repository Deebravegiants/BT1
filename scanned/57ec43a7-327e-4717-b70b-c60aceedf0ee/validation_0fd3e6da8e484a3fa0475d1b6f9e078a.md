### Title
LP Share Burn With Zero Token Return Due to Rounding in `removeLiquidity` — (`metric-core/contracts/libraries/LiquidityLib.sol`)

### Summary

`LiquidityLib.removeLiquidity` computes the token amounts owed to a withdrawing LP using integer floor division. When the bin's scaled balance is small relative to total shares, both `amount0Scaled` and `amount1Scaled` round to zero. The function still burns the user's shares and decrements `binTotalShares`, so the LP permanently loses their position while receiving nothing. The remaining LPs silently absorb the forfeited balance.

### Finding Description

In `LiquidityLib.removeLiquidity`, the per-bin token amounts owed to the withdrawing LP are computed as:

```solidity
uint256 amount0Scaled = _checkedMul(binState.token0BalanceScaled, sharesToRemove) / binTotalSharesVal;
uint256 amount1Scaled = _checkedMul(binState.token1BalanceScaled, sharesToRemove) / binTotalSharesVal;
``` [1](#0-0) 

This is a plain floor division. When `binState.token0BalanceScaled * sharesToRemove < binTotalSharesVal`, the result is zero. Immediately after, the code unconditionally updates state:

```solidity
binState.token0BalanceScaled -= uint104(amount0Scaled);   // subtracts 0
binState.token1BalanceScaled -= uint104(amount1Scaled);   // subtracts 0
binTotalShares[binIdx] = binTotalSharesVal - sharesToRemove; // shares burned
positionBinShares[posKey] = newUserShares;                   // user position cleared
``` [2](#0-1) 

There is no guard that reverts or skips the state update when both computed amounts are zero. The function then converts scaled amounts to external units with `Math.Rounding.Floor`:

```solidity
(amount0Removed, amount1Removed) =
  _deltasScaledToExternal(totalToken0ToRemoveScaled, totalToken1ToRemoveScaled, ctx, Math.Rounding.Floor);
``` [3](#0-2) 

and only transfers tokens when the result is non-zero:

```solidity
if (amount0Removed > 0) { IERC20(ctx.token0).safeTransfer(owner, amount0Removed); }
if (amount1Removed > 0) { IERC20(ctx.token1).safeTransfer(owner, amount1Removed); }
``` [4](#0-3) 

The LP's shares are gone; the bin balance is unchanged; the remaining LPs' proportional claim on that balance increases.

A second rounding point exists in `_deltasScaledToExternal` itself: even if `amount0Scaled > 0`, dividing by `TOKEN_0_SCALE_MULTIPLIER` (up to `10^12` for a 6-decimal token) can produce zero external units, again with no revert. [5](#0-4) 

### Impact Explanation

An LP who calls `removeLiquidity` under the triggering conditions permanently loses their entire position in the affected bin. Their shares are burned, the bin balance is not reduced, and no tokens are transferred. The forfeited balance is redistributed to remaining LPs. This is a direct, irreversible loss of user principal — the exact impact class required by the allowed-impact gate (broken LP withdraw flow causing loss of LP assets).

### Likelihood Explanation

The condition `binState.token0BalanceScaled * sharesToRemove < binTotalSharesVal` is reachable in normal operation:

- A bin that has been heavily traded can have its balance drained to a few scaled units while retaining many LP shares (shares are not affected by swaps).
- A small LP (holding the minimum `minimalMintableLiquidity` shares) removing their full position in such a bin will trigger the rounding.
- The `minimalMintableLiquidity` check only prevents leaving a dust *position*; it does not prevent a full removal that yields zero tokens. [6](#0-5) 

Because `removeLiquidity` requires `msg.sender == owner`, the attack cannot be forced on a victim by a third party. However, the user can trigger it unknowingly (e.g., via a router that does not pre-simulate the output), and there is no on-chain protection.

### Recommendation

Add a revert (or at minimum a zero-output guard) before burning shares when both computed amounts are zero:

```solidity
uint256 amount0Scaled = _checkedMul(binState.token0BalanceScaled, sharesToRemove) / binTotalSharesVal;
uint256 amount1Scaled = _checkedMul(binState.token1BalanceScaled, sharesToRemove) / binTotalSharesVal;

// Guard: never burn shares for zero return
if (amount0Scaled == 0 && amount1Scaled == 0) {
    revert ZeroTokensOut();
}
```

Alternatively, use `Math.ceilDiv` for the LP's share of the bin balance (rounding in the LP's favour, consistent with how `addLiquidity` rounds against the LP):

```solidity
uint256 amount0Scaled = Math.ceilDiv(_checkedMul(binState.token0BalanceScaled, sharesToRemove), binTotalSharesVal);
uint256 amount1Scaled = Math.ceilDiv(_checkedMul(binState.token1BalanceScaled, sharesToRemove), binTotalSharesVal);
```

Note that `addLiquidity` already uses `Math.ceilDiv` to charge the LP on deposit, so using floor on withdrawal creates an asymmetric rounding that always favours the pool over the LP. [7](#0-6) 

### Proof of Concept

**Setup:**
- Pool with a 6-decimal token (USDC) as token0; `TOKEN_0_SCALE_MULTIPLIER = 1e12`.
- Bin 0 has been traded down to `token0BalanceScaled = 500` (0.0000000005 USDC in external units).
- `binTotalShares[0] = 1_000_000e18` (many LPs, each holding `minimalMintableLiquidity = 1e18` shares).
- Alice holds `1e18` shares in bin 0.

**Attack / accidental trigger:**
1. Alice calls `removeLiquidity` with `sharesToRemove = 1e18` (her full position).
2. `amount0Scaled = (500 * 1e18) / 1_000_000e18 = 500 / 1_000_000 = 0`.
3. `amount1Scaled = 0` (bin has no token1 at this point).
4. `binState.token0BalanceScaled -= 0` → unchanged at 500.
5. `binTotalShares[0] = 1_000_000e18 - 1e18 = 999_999e18`.
6. `positionBinShares[aliceKey] = 0` → Alice's position is erased.
7. `amount0Removed = 0 / 1e12 = 0`; no transfer.
8. Alice receives nothing. The 500 scaled units (worth ~0.0000000005 USDC) remain in the bin and are now owned by the remaining 999,999 LPs.

While the absolute token value lost per event is small, the shares burned represent Alice's full proportional claim on future bin earnings and any future balance growth from swaps. The pattern can be repeated across multiple bins or exploited by an LP who deliberately seeds a bin with dust to grief other small LPs.

### Citations

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L109-110)
```text
            amount0Scaled = Math.ceilDiv(_checkedMul(binState.token0BalanceScaled, sharesToAdd), binTotalSharesVal);
            amount1Scaled = Math.ceilDiv(_checkedMul(binState.token1BalanceScaled, sharesToAdd), binTotalSharesVal);
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L199-202)
```text
          uint256 newUserShares = userShares - sharesToRemove;
          if (newUserShares > 0 && newUserShares < ctx.minimalMintableLiquidity) {
            revert IMetricOmmPoolActions.MinimalLiquidity(newUserShares, ctx.minimalMintableLiquidity);
          }
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L205-206)
```text
          uint256 amount0Scaled = _checkedMul(binState.token0BalanceScaled, sharesToRemove) / binTotalSharesVal;
          uint256 amount1Scaled = _checkedMul(binState.token1BalanceScaled, sharesToRemove) / binTotalSharesVal;
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L210-214)
```text
          binState.token0BalanceScaled -= uint104(amount0Scaled);
          // forge-lint: disable-next-line(unsafe-typecast)
          binState.token1BalanceScaled -= uint104(amount1Scaled);
          binTotalShares[binIdx] = binTotalSharesVal - sharesToRemove;
          positionBinShares[posKey] = newUserShares;
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L239-240)
```text
      (amount0Removed, amount1Removed) =
        _deltasScaledToExternal(totalToken0ToRemoveScaled, totalToken1ToRemoveScaled, ctx, Math.Rounding.Floor);
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L242-246)
```text
      if (amount0Removed > 0) {
        IERC20(ctx.token0).safeTransfer(owner, amount0Removed);
      }
      if (amount1Removed > 0) {
        IERC20(ctx.token1).safeTransfer(owner, amount1Removed);
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L274-276)
```text
    } else {
      deltaAmount0 = scaledDeltaAmount0 / ctx.token0ScaleMultiplier;
      deltaAmount1 = scaledDeltaAmount1 / ctx.token1ScaleMultiplier;
```
