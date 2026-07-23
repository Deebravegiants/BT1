Based on my analysis of the codebase, I have identified a valid analog to the external report.

---

### Title
Missing Slippage Protection on `removeLiquidity` with No Periphery Wrapper — (`metric-core/contracts/MetricOmmPool.sol`, `metric-core/contracts/libraries/LiquidityLib.sol`)

### Summary

`removeLiquidity` on `MetricOmmPool` accepts only a share-burn delta and returns whatever token amounts the bins currently hold. There are no `minAmount0Out` / `minAmount1Out` guard parameters, and — unlike `addLiquidity`, which has `MetricOmmPoolLiquidityAdder` with `maxAmountToken0`/`maxAmountToken1` caps — no periphery wrapper exists for removal. Because `msg.sender == owner` is enforced, LPs must call the pool directly with zero ability to reject an unfavourable token composition at execution time.

### Finding Description

`MetricOmmPool.removeLiquidity` delegates to `LiquidityLib.removeLiquidity`. The token amounts returned are computed purely from the live bin state at execution time:

```solidity
uint256 amount0Scaled = _checkedMul(binState.token0BalanceScaled, sharesToRemove) / binTotalSharesVal;
uint256 amount1Scaled = _checkedMul(binState.token1BalanceScaled, sharesToRemove) / binTotalSharesVal;
``` [1](#0-0) 

These values depend on `binState.token0BalanceScaled` and `binState.token1BalanceScaled`, which are mutated by every swap that traverses the bin. A swap that fully drains token0 from a bin leaves the LP with 100 % token1 on removal, regardless of what composition the LP observed when they signed the transaction. [2](#0-1) 

The pool-level function signature is:

```solidity
function removeLiquidity(address owner, uint80 salt, LiquidityDelta calldata deltas, bytes calldata extensionData)
    external
    returns (uint256 amount0Removed, uint256 amount1Removed);
``` [3](#0-2) 

No `minAmount0Out` or `minAmount1Out` parameter exists anywhere in the call chain.

By contrast, `addLiquidity` is protected: `MetricOmmPoolLiquidityAdder` stores `maxAmountToken0` / `maxAmountToken1` in transient storage and reverts with `MaxAmountExceeded` if the pool requests more than the caller's caps. [4](#0-3) 

No equivalent periphery wrapper exists for `removeLiquidity`. The periphery directory contains only `MetricOmmPoolLiquidityAdder` (add-only) and `MetricOmmSimpleRouter` (swaps only). [5](#0-4) 

Because `removeLiquidity` enforces `msg.sender == owner`, the LP cannot route through any intermediary that could add the missing guard:

```solidity
if (msg.sender != owner) revert NotPositionOwner();
``` [6](#0-5) 

### Impact Explanation

An LP who observes a 50/50 token0/token1 composition in their bin and submits a `removeLiquidity` transaction may receive 100 % of the lower-value token if swaps drain the other token before the transaction lands. The LP has no on-chain mechanism to reject this outcome. The total USD value received can differ materially from the value at decision time, constituting a direct loss of LP principal relative to their expectation and relative to what they would have received had they been able to set minimum output bounds.

### Likelihood Explanation

Any active pool with non-trivial swap volume creates the condition. The window between transaction submission and inclusion is sufficient for one or more swaps to shift bin composition. No privileged access is required; normal swap activity by any user is the trigger. The LP's only recourse is off-chain monitoring and transaction cancellation, which is unreliable under mempool congestion.

### Recommendation

1. Add `minAmount0Out` and `minAmount1Out` parameters to `removeLiquidity` at the pool level, reverting if the computed amounts fall below the caller's bounds.
2. Alternatively, add a periphery `MetricOmmPoolLiquidityRemover` contract that wraps `removeLiquidity` with post-execution minimum-output checks — analogous to how `MetricOmmPoolLiquidityAdder` wraps `addLiquidity` with maximum-input caps. This requires relaxing the `msg.sender == owner` constraint to allow an approved operator, or having the LP call the wrapper directly as owner.

### Proof of Concept

1. LP holds 1 000 shares in bin 0, which currently holds 500 scaled token0 and 500 scaled token1 (50/50 split). LP submits `removeLiquidity` expecting ~500 of each token.
2. Before the LP's transaction lands, a large swap (`zeroForOne = false`, buying token0 with token1) traverses bin 0, draining all `token0BalanceScaled` and filling `token1BalanceScaled`.
3. LP's transaction executes. `LiquidityLib.removeLiquidity` computes:
   - `amount0Scaled = (0 * 1000) / totalShares = 0`
   - `amount1Scaled = (1000 * 1000) / totalShares = 1000`
4. LP receives 0 token0 and ~1 000 token1. If token0 is the more valuable asset at current oracle price, the LP has suffered a direct loss relative to their expectation, with no on-chain recourse. [7](#0-6)

### Citations

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

**File:** metric-core/contracts/interfaces/IMetricOmmPool/IMetricOmmPoolActions.sol (L172-174)
```text
  function removeLiquidity(address owner, uint80 salt, LiquidityDelta calldata deltas, bytes calldata extensionData)
    external
    returns (uint256 amount0Removed, uint256 amount1Removed);
```

**File:** metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol (L165-167)
```text
    if (amount0Delta > max0 || amount1Delta > max1) {
      revert MaxAmountExceeded(amount0Delta, amount1Delta, max0, max1);
    }
```

**File:** metric-core/contracts/MetricOmmPool.sol (L199-212)
```text
  function removeLiquidity(address owner, uint80 salt, LiquidityDelta calldata deltas, bytes calldata extensionData)
    external
    nonReentrant(PoolActions.REMOVE_LIQUIDITY)
    returns (uint256 amount0Removed, uint256 amount1Removed)
  {
    if (deltas.binIdxs.length == 0) return (0, 0);
    if (deltas.binIdxs.length != deltas.shares.length) revert LiquidityDeltaLengthMismatch();
    if (msg.sender != owner) revert NotPositionOwner();
    _beforeRemoveLiquidity(msg.sender, owner, salt, deltas, extensionData);
    (amount0Removed, amount1Removed) = LiquidityLib.removeLiquidity(
      _liquidityContext(), owner, salt, deltas, binTotals, _binStates, _binTotalShares, _positionBinShares
    );
    _afterRemoveLiquidity(msg.sender, owner, salt, deltas, amount0Removed, amount1Removed, extensionData);
  }
```
