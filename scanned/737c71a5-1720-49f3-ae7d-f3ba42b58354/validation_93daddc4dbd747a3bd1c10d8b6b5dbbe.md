### Title
Missing Slippage Protection in `removeLiquidity` Exposes LPs to Front-Running Token Composition Attacks — (File: metric-core/contracts/MetricOmmPool.sol, metric-core/contracts/libraries/LiquidityLib.sol)

---

### Summary

`MetricOmmPool.removeLiquidity` accepts no minimum-output-amount parameters, and no periphery wrapper adds them. A swap executed before the LP's removal transaction settles directly mutates the bin's `token0BalanceScaled` / `token1BalanceScaled`, changing the token composition the LP receives. The LP has no on-chain mechanism to revert if the returned amounts fall below their acceptable threshold.

---

### Finding Description

`MetricOmmPool.removeLiquidity` signature:

```solidity
function removeLiquidity(
    address owner,
    uint80 salt,
    LiquidityDelta calldata deltas,
    bytes calldata extensionData
) external nonReentrant(PoolActions.REMOVE_LIQUIDITY)
  returns (uint256 amount0Removed, uint256 amount1Removed)
``` [1](#0-0) 

There are no `minAmount0Out` / `minAmount1Out` parameters. The function delegates directly to `LiquidityLib.removeLiquidity`, which computes the LP's share of each token from the live bin state and immediately transfers:

```solidity
uint256 amount0Scaled = _checkedMul(binState.token0BalanceScaled, sharesToRemove) / binTotalSharesVal;
uint256 amount1Scaled = _checkedMul(binState.token1BalanceScaled, sharesToRemove) / binTotalSharesVal;
...
IERC20(ctx.token0).safeTransfer(owner, amount0Removed);
IERC20(ctx.token1).safeTransfer(owner, amount1Removed);
``` [2](#0-1) 

Swaps directly mutate `binState.token0BalanceScaled` and `binState.token1BalanceScaled` in storage via `_saveBinState`. For example, a `buyToken0InBinSpecifiedOut` step:

```solidity
binState.token0BalanceScaled -= amountOutScaled.toUint104();
binState.token1BalanceScaled = (uint256(binState.token1BalanceScaled) + amountInScaled - protocolFeeAmountScaled).toUint104();
``` [3](#0-2) 

The periphery `MetricOmmPoolLiquidityAdder` provides `maxAmountToken0` / `maxAmountToken1` caps for `addLiquidity` enforced in the callback, and `addLiquidityWeighted` adds cursor-bound guards (`minimalCurBin`, `maximalCurBin`). **No equivalent periphery contract or wrapper exists for `removeLiquidity`.** [4](#0-3) 

---

### Impact Explanation

An LP holding shares in the current bin (bin 0) expects a proportional mix of token0 and token1 based on `curPosInBin`. A swap that traverses the current bin before the LP's removal settles will shift `token0BalanceScaled` down and `token1BalanceScaled` up (or vice versa). The LP then receives a composition they did not consent to — potentially receiving all of one token when they expected a mix — with no on-chain revert path. If the LP's intended use requires a specific token (e.g., they need token0 to repay a loan), they must execute an additional swap at market cost, incurring spread fees and price impact. This constitutes a direct, measurable reduction in the value of LP principal recovered.

---

### Likelihood Explanation

Any swap caller can front-run a pending `removeLiquidity` transaction visible in the mempool. No special privilege is required. The attacker pays oracle-priced swap fees but profits from the LP's forced composition change if they back-run to restore the cursor. On chains with public mempools (Ethereum mainnet, most L2s without private RPCs), this is straightforward to execute. Likelihood is **medium** — it requires mempool visibility and a willing attacker, but the mechanism is standard MEV.

---

### Recommendation

1. Add `minAmount0Out` and `minAmount1Out` parameters to `MetricOmmPool.removeLiquidity` and enforce them after `LiquidityLib.removeLiquidity` returns:

```solidity
function removeLiquidity(
    address owner,
    uint80 salt,
    LiquidityDelta calldata deltas,
    uint256 minAmount0Out,   // <-- add
    uint256 minAmount1Out,   // <-- add
    bytes calldata extensionData
) external ...
{
    ...
    (amount0Removed, amount1Removed) = LiquidityLib.removeLiquidity(...);
    if (amount0Removed < minAmount0Out || amount1Removed < minAmount1Out)
        revert SlippageExceeded();
    ...
}
```

2. Alternatively, add a periphery `MetricOmmPoolLiquidityRemover` contract analogous to `MetricOmmPoolLiquidityAdder` that wraps `removeLiquidity` with minimum-output checks and a deadline, so EOAs have a safe path without modifying the core interface.

---

### Proof of Concept

**Setup:** Pool with bins [-1, 0, 1]. Bin 0 is the current bin with `curPosInBin = type(uint104).max / 2` (50% through), holding both token0 and token1. LP holds 10 000 shares in bin 0.

**Attack sequence:**

1. LP broadcasts `removeLiquidity(owner, salt, [{binIdx: 0, shares: 10000}], "")`.
2. Attacker sees the transaction in the mempool and front-runs with `swap(zeroForOne=false, amountSpecified=large, ...)` — buying all available token0 from bin 0, moving `curPosInBin` to `type(uint104).max` and draining `token0BalanceScaled` to near zero while filling `token1BalanceScaled`.
3. LP's `removeLiquidity` executes. `LiquidityLib` reads the now-modified bin state:
   - `amount0Scaled = binState.token0BalanceScaled * 10000 / binTotalShares ≈ 0`
   - `amount1Scaled = binState.token1BalanceScaled * 10000 / binTotalShares ≈ full token1 share`
4. LP receives ~0 token0 and all token1. If the LP needed token0, they must now swap token1 → token0 at oracle spread cost.
5. Attacker back-runs with the reverse swap to restore the cursor, profiting from the round-trip spread.

The LP had no parameter to revert this outcome. With a `minAmount0Out` guard, step 3 would have reverted, protecting the LP. [5](#0-4) [1](#0-0)

### Citations

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

**File:** metric-core/contracts/libraries/SwapMath.sol (L413-415)
```text
      binState.token0BalanceScaled -= amountOutScaled.toUint104();
      binState.token1BalanceScaled =
        (uint256(binState.token1BalanceScaled) + amountInScaled - protocolFeeAmountScaled).toUint104();
```

**File:** metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol (L56-81)
```text
  function addLiquidityExactShares(
    address pool,
    address owner,
    uint80 salt,
    LiquidityDelta calldata deltas,
    uint256 maxAmountToken0,
    uint256 maxAmountToken1,
    bytes calldata extensionData
  ) external payable override returns (uint256 amount0Added, uint256 amount1Added) {
    _validateOwner(owner);
    _validateDeltas(deltas);
    return _addLiquidity(pool, owner, salt, deltas, msg.sender, maxAmountToken0, maxAmountToken1, extensionData);
  }

  /// @notice Add liquidity with explicit per-bin shares for `msg.sender`.
  function addLiquidityExactShares(
    address pool,
    uint80 salt,
    LiquidityDelta calldata deltas,
    uint256 maxAmountToken0,
    uint256 maxAmountToken1,
    bytes calldata extensionData
  ) external payable override returns (uint256 amount0Added, uint256 amount1Added) {
    _validateDeltas(deltas);
    return _addLiquidity(pool, msg.sender, salt, deltas, msg.sender, maxAmountToken0, maxAmountToken1, extensionData);
  }
```
