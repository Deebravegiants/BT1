### Title
Free Share Minting in Fully-Drained Bins Dilutes Existing LP Claims - (`metric-core/contracts/libraries/LiquidityLib.sol`)

### Summary
When a swap fully drains a bin's token balances to zero while `binTotalShares` remains non-zero, any caller can invoke `addLiquidity` to mint an arbitrary number of shares in that bin without depositing any tokens. The proportional token calculation yields zero when the bin balance is zero, causing the settlement callback to be skipped while shares are unconditionally credited. When a reverse swap later refills the bin, the attacker's free shares entitle them to a proportional claim on the new tokens, directly stealing LP principal.

### Finding Description

In `LiquidityLib.addLiquidity`, when `binTotalSharesVal > 0` (existing shareholders), the required token amounts are computed proportionally:

```solidity
amount0Scaled = Math.ceilDiv(_checkedMul(binState.token0BalanceScaled, sharesToAdd), binTotalSharesVal);
amount1Scaled = Math.ceilDiv(_checkedMul(binState.token1BalanceScaled, sharesToAdd), binTotalSharesVal);
```

If a swap has fully drained the bin (`token0BalanceScaled == 0` and `token1BalanceScaled == 0`), both amounts evaluate to `Math.ceilDiv(0, binTotalSharesVal) = 0`. The settlement callback is then skipped entirely:

```solidity
if (amount0Added > 0 || amount1Added > 0) {
    // callback NOT invoked — no tokens pulled from caller
}
```

However, shares are **unconditionally** minted regardless:

```solidity
binTotalShares[binIdx] = binTotalSharesVal + sharesToAdd;
positionBinShares[posKey] = newUserShares;
```

There is no guard preventing share minting when the bin is drained. The only check is `minimalMintableLiquidity`, which is a dust floor, not a token-deposit requirement. The `binTotals` accounting is also not updated (since `totalToken0ToAddScaled == 0`), so the pool's balance accounting appears correct while the share registry is corrupted.

A bin above the current price holds only token0; a large `zeroForOne` swap can consume all of it, leaving `token0BalanceScaled = 0` and `token1BalanceScaled = 0` while `binTotalShares` is unchanged. The same applies to below-price bins (token1 only) and the current bin (both tokens). This is a reachable state in normal pool operation. [1](#0-0) [2](#0-1) 

### Impact Explanation

When a reverse swap later refills the drained bin, the attacker's free shares entitle them to a proportional claim on the incoming tokens. Existing LPs receive fewer tokens than they are owed — a direct loss of LP principal. The attacker can scale the attack by minting an arbitrarily large number of shares (e.g., minting 1,000,000 shares against 10,000 existing shares captures ~99% of future refill tokens). This constitutes pool insolvency from the LP's perspective: the pool's token balance is correct, but the share registry no longer accurately represents LP entitlements.

### Likelihood Explanation

Any swap that fully drains a bin creates this window. Large swaps or swaps in low-liquidity bins routinely drain bins completely during normal operation. The attacker monitors the chain for `BinSwapped` events showing a bin balance reaching zero, then calls `addLiquidity` in the next block. No special permissions or privileged access are required — `addLiquidity` is fully permissionless. [3](#0-2) 

### Recommendation

In `LiquidityLib.addLiquidity`, when `binTotalSharesVal > 0` and both `token0BalanceScaled == 0` and `token1BalanceScaled == 0`, either:

1. **Revert** with a new error (e.g., `DrainedBin`) to prevent free minting entirely, or
2. **Fall back to the initial per-share rate** (the same path used when `binTotalSharesVal == 0`) so that tokens proportional to `initialScaledToken0PerShareE18` / `initialScaledToken1PerShareE18` are required.

```solidity
// Proposed guard inside the binTotalSharesVal > 0 branch:
if (binState.token0BalanceScaled == 0 && binState.token1BalanceScaled == 0) {
    revert DrainedBin(binIdx);
}
``` [4](#0-3) 

### Proof of Concept

1. **LP1** calls `addLiquidity` for bin `X` (above current price, token0-only): `token0BalanceScaled = 1000`, `binTotalShares[X] = 10000`.
2. A large `zeroForOne` swap fully consumes bin `X`: `token0BalanceScaled = 0`, `binTotalShares[X] = 10000` (unchanged by swap).
3. **Attacker** calls `addLiquidity` for bin `X` with `sharesToAdd = 10000`:
   - `amount0Scaled = Math.ceilDiv(0 * 10000 / 10000) = 0`
   - `amount1Scaled = 0`
   - `amount0Added = 0`, `amount1Added = 0` → callback skipped, zero tokens paid
   - `binTotalShares[X] = 20000`, `positionBinShares[attacker][X] = 10000`
4. A reverse swap refills bin `X` with 1000 token0 (updating `token0BalanceScaled = 1000`).
5. **LP1** calls `removeLiquidity`: receives `10000 * 1000 / 20000 = 500` token0 (should be 1000).
6. **Attacker** calls `removeLiquidity`: receives `10000 * 1000 / 20000 = 500` token0 at zero cost.

LP1 loses 500 token0 of principal to the attacker. The attacker can amplify the attack by minting far more shares than the existing total. [5](#0-4) [6](#0-5)

### Citations

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L85-131)
```text
          if (binTotalSharesVal == 0) {
            if (binIdx < curBinIdxCache) {
              amount1Scaled = Math.ceilDiv(_checkedMul(ctx.initialScaledToken1PerShareE18, sharesToAdd), 1e18);
            } else if (binIdx > curBinIdxCache) {
              amount0Scaled = Math.ceilDiv(_checkedMul(ctx.initialScaledToken0PerShareE18, sharesToAdd), 1e18);
            } else {
              uint256 token0Proportion = type(uint104).max - ctx.curPosInBin;
              uint256 token1Proportion = ctx.curPosInBin;
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
            }
          } else {
            amount0Scaled = Math.ceilDiv(_checkedMul(binState.token0BalanceScaled, sharesToAdd), binTotalSharesVal);
            amount1Scaled = Math.ceilDiv(_checkedMul(binState.token1BalanceScaled, sharesToAdd), binTotalSharesVal);
          }
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

          binBalanceDeltas[i] = BinBalanceDelta({
            // Safe: per-bin deltas are bounded by uint104 bin balances.
            // forge-lint: disable-next-line(unsafe-typecast)
            delta0Scaled: int256(amount0Scaled),
            // casting to int256 is safe because amount1Scaled is bounded by uint104 bin balances.
            // forge-lint: disable-next-line(unsafe-typecast)
            delta1Scaled: int256(amount1Scaled)
          });
        }
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

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L196-214)
```text
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
```

**File:** metric-core/contracts/MetricOmmPool.sol (L182-196)
```text
  function addLiquidity(
    address owner,
    uint80 salt,
    LiquidityDelta calldata deltas,
    bytes calldata callbackData,
    bytes calldata extensionData
  ) external nonReentrant(PoolActions.ADD_LIQUIDITY) returns (uint256 amount0Added, uint256 amount1Added) {
    if (deltas.binIdxs.length == 0) return (0, 0);
    if (deltas.binIdxs.length != deltas.shares.length) revert LiquidityDeltaLengthMismatch();
    _beforeAddLiquidity(msg.sender, owner, salt, deltas, extensionData);
    (amount0Added, amount1Added) = LiquidityLib.addLiquidity(
      _liquidityContext(), owner, salt, deltas, callbackData, binTotals, _binStates, _binTotalShares, _positionBinShares
    );
    _afterAddLiquidity(msg.sender, owner, salt, deltas, amount0Added, amount1Added, extensionData);
  }
```
