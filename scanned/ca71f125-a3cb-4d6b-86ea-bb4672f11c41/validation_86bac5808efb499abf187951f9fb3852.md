### Title
LP Shares Burned With Zero Token Return Due to Floor Division Truncation in `removeLiquidity` - (File: `metric-core/contracts/libraries/LiquidityLib.sol`)

### Summary

`LiquidityLib.removeLiquidity` computes the token amounts owed to an LP using plain integer floor division. When a bin's scaled token balance is small relative to total shares (a state reachable through normal swap activity), the division truncates to zero, burning the LP's shares while returning no tokens.

### Finding Description

In `LiquidityLib.removeLiquidity`, the per-bin token amounts owed to the withdrawing LP are computed as:

```solidity
uint256 amount0Scaled = _checkedMul(binState.token0BalanceScaled, sharesToRemove) / binTotalSharesVal;
uint256 amount1Scaled = _checkedMul(binState.token1BalanceScaled, sharesToRemove) / binTotalSharesVal;
``` [1](#0-0) 

Both divisions are plain floor divisions with no zero-output guard. When `binState.token0BalanceScaled * sharesToRemove < binTotalSharesVal`, `amount0Scaled` evaluates to `0`. The code then proceeds to:

1. Subtract `0` from `binState.token0BalanceScaled` (no change to pool balance)
2. Reduce `binTotalShares[binIdx]` by `sharesToRemove`
3. Reduce `positionBinShares[posKey]` by `sharesToRemove`
4. Transfer `0` tokens to the LP owner [2](#0-1) 

The LP's shares are permanently burned, but the tokens they represented remain in the pool and are redistributed to remaining LPs.

**How the vulnerable state arises naturally:**

When a bin is first seeded, `token0BalanceScaled` and `binTotalShares` are proportional (both grow together via `ceilDiv` in `addLiquidity`). [3](#0-2) 

Swaps, however, consume `token0BalanceScaled` without touching `binTotalShares`. After heavy trading through a bin, the bin can reach a state such as `token0BalanceScaled = 1`, `binTotalShares = 10000`. An LP removing 9999 of their 10000 shares computes `(1 * 9999) / 10000 = 0` and receives nothing.

The existing `minimalMintableLiquidity` guard only prevents leaving a dust *position* (non-zero `newUserShares < minimalMintableLiquidity`); it does not prevent removing shares that yield zero tokens. [4](#0-3) 

### Impact Explanation

Direct loss of LP principal. The LP burns valid shares and receives zero tokens in return. The forfeited tokens accrue to remaining LPs in the same bin. This is a silent, irreversible transfer of value from the withdrawing LP to other LPs, triggered by normal pool operation (swaps depleting a bin's balance).

### Likelihood Explanation

Any bin that has been the active trading bin and has had its token balance significantly depleted by swaps is vulnerable. No privileged access, malicious setup, or non-standard tokens are required. The condition arises organically in any pool with active trading volume. An LP who adds liquidity early, waits for swaps to deplete the bin, and then removes liquidity will silently lose their remaining token claim.

### Recommendation

Add a zero-output guard in `removeLiquidity`. If `sharesToRemove > 0` and the bin has a non-zero token balance, the computed `amount0Scaled` (or `amount1Scaled`) must not be zero. Either:

1. Revert with a descriptive error (e.g., `ZeroTokenReturn`) when `amount0Scaled == 0 && binState.token0BalanceScaled > 0`, forcing the LP to remove a larger share batch or wait for the bin to be replenished.
2. Use `Math.ceilDiv` for the LP's benefit (gives the LP at least 1 scaled unit when their proportional share rounds down), consistent with how `addLiquidity` uses `ceilDiv` to protect the pool.

Option 1 is safer as it preserves pool accounting integrity.

### Proof of Concept

```
Initial state:
  binTotalShares[0]          = 10_000
  binState.token0BalanceScaled = 10_000   (1:1 ratio after initial deposit)

After swaps consume all but 1 unit of token0:
  binTotalShares[0]          = 10_000   (unchanged by swaps)
  binState.token0BalanceScaled = 1

LP removes 9_999 shares (leaving 1 share, which passes minimalMintableLiquidity = 1000? No — 
if minimalMintableLiquidity = 1000, the LP must leave >= 1000 shares or remove all.
So LP removes all 10_000 shares):

  amount0Scaled = (1 * 10_000) / 10_000 = 1   ← LP gets 1 unit (OK in this case)

But with binTotalShares = 100_000 (second LP added more shares after the swap):
  amount0Scaled = (1 * 10_000) / 100_000 = 0  ← LP burns 10_000 shares, receives 0 tokens

Result: LP's 10_000 shares are burned, pool retains the token0, 
        remaining LPs receive the forfeited value.
```

The scenario with `binTotalShares >> token0BalanceScaled` is reachable whenever a second LP adds shares to a bin that has already been heavily traded through, increasing `binTotalShares` while `token0BalanceScaled` remains near zero. [5](#0-4)

### Citations

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L109-110)
```text
            amount0Scaled = Math.ceilDiv(_checkedMul(binState.token0BalanceScaled, sharesToAdd), binTotalSharesVal);
            amount1Scaled = Math.ceilDiv(_checkedMul(binState.token1BalanceScaled, sharesToAdd), binTotalSharesVal);
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L161-251)
```text
  function removeLiquidity(
    PoolContext memory ctx,
    address owner,
    uint80 salt,
    LiquidityDelta calldata deltas,
    BinTotals storage binTotals,
    mapping(int256 => BinState) storage binStates,
    mapping(int256 => uint256) storage binTotalShares,
    mapping(bytes32 => uint256) storage positionBinShares
  ) public returns (uint256 amount0Removed, uint256 amount1Removed) {
    unchecked {
      uint256 length = deltas.binIdxs.length;
      if (length == 0) return (0, 0);

      uint256 totalToken0ToRemoveScaled = 0;
      uint256 totalToken1ToRemoveScaled = 0;

      BinBalanceDelta[] memory binBalanceDeltas = new BinBalanceDelta[](length);

      for (uint256 i = 0; i < length; i++) {
        int256 binIdx = deltas.binIdxs[i];
        uint256 sharesToRemove = deltas.shares[i];

        if (binIdx < ctx.lowestBin || binIdx > ctx.highestBin) {
          revert IMetricOmmPoolActions.InvalidBinIndex(binIdx);
        }
        if (sharesToRemove == 0) continue;

        {
          // safe because -128 <= LOWEST_BIN <= HIGHEST_BIN <= 127 (enforced by factory)
          // forge-lint: disable-next-line(unsafe-typecast)
          bytes32 posKey = _positionBinKey(owner, salt, int8(binIdx));
          uint256 binTotalSharesVal = binTotalShares[binIdx];
          uint256 userShares = positionBinShares[posKey];

          if (userShares < sharesToRemove) {
            revert IMetricOmmPoolActions.InsufficientLiquidity(sharesToRemove, userShares);
          }
          uint256 newUserShares = userShares - sharesToRemove;
          if (newUserShares > 0 && newUserShares < ctx.minimalMintableLiquidity) {
            revert IMetricOmmPoolActions.MinimalLiquidity(newUserShares, ctx.minimalMintableLiquidity);
          }

          BinState storage binState = binStates[binIdx];
          uint256 amount0Scaled = _checkedMul(binState.token0BalanceScaled, sharesToRemove) / binTotalSharesVal;
          uint256 amount1Scaled = _checkedMul(binState.token1BalanceScaled, sharesToRemove) / binTotalSharesVal;

          // casting to uint104 is safe because amount0Scaled and amount1Scaled are less than token(0|1)BalanceScaled
          // forge-lint: disable-next-line(unsafe-typecast)
          binState.token0BalanceScaled -= uint104(amount0Scaled);
          // forge-lint: disable-next-line(unsafe-typecast)
          binState.token1BalanceScaled -= uint104(amount1Scaled);
          binTotalShares[binIdx] = binTotalSharesVal - sharesToRemove;
          positionBinShares[posKey] = newUserShares;

          totalToken0ToRemoveScaled += amount0Scaled;
          totalToken1ToRemoveScaled += amount1Scaled;

          binBalanceDeltas[i] = BinBalanceDelta({
            // safe because amount0Scaled is bounded by uint104 bin balances.
            // forge-lint: disable-next-line(unsafe-typecast)
            delta0Scaled: -int256(amount0Scaled),
            // safe because amount1Scaled is bounded by uint104 bin balances.
            // forge-lint: disable-next-line(unsafe-typecast)
            delta1Scaled: -int256(amount1Scaled)
          });
        }
      }

      if (totalToken0ToRemoveScaled > 0) {
        // forge-lint: disable-next-line(unsafe-typecast)
        binTotals.scaledToken0 = uint128(uint256(binTotals.scaledToken0) - totalToken0ToRemoveScaled);
      }
      if (totalToken1ToRemoveScaled > 0) {
        // forge-lint: disable-next-line(unsafe-typecast)
        binTotals.scaledToken1 = uint128(uint256(binTotals.scaledToken1) - totalToken1ToRemoveScaled);
      }

      (amount0Removed, amount1Removed) =
        _deltasScaledToExternal(totalToken0ToRemoveScaled, totalToken1ToRemoveScaled, ctx, Math.Rounding.Floor);

      if (amount0Removed > 0) {
        IERC20(ctx.token0).safeTransfer(owner, amount0Removed);
      }
      if (amount1Removed > 0) {
        IERC20(ctx.token1).safeTransfer(owner, amount1Removed);
      }

      emit IMetricOmmPoolActions.LiquidityRemoved(owner, salt, deltas.binIdxs, binBalanceDeltas, deltas.shares);
    }
  }
```
