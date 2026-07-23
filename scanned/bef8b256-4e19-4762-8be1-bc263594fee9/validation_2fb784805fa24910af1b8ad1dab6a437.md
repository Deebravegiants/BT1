### Title
Missing Minimum-Output Protection in `removeLiquidity()` Exposes LP Withdrawals to Composition Slippage — (`metric-core/contracts/MetricOmmPool.sol`, `metric-core/contracts/libraries/LiquidityLib.sol`)

---

### Summary

`MetricOmmPool.removeLiquidity()` burns a caller-specified share count and transfers the proportional bin balances directly to `owner` with no minimum-token-output guard and no deadline. No periphery wrapper exists that adds these guards. A pending withdrawal can execute after swaps have shifted the current bin's composition, delivering far less of one token than the LP expected, with no on-chain recourse.

---

### Finding Description

`MetricOmmPool.removeLiquidity()` accepts a `LiquidityDelta` (bins + shares to burn) and returns `(amount0Removed, amount1Removed)` computed inside `LiquidityLib.removeLiquidity()`:

```solidity
uint256 amount0Scaled = _checkedMul(binState.token0BalanceScaled, sharesToRemove) / binTotalSharesVal;
uint256 amount1Scaled = _checkedMul(binState.token1BalanceScaled, sharesToRemove) / binTotalSharesVal;
``` [1](#0-0) 

The amounts are then transferred unconditionally:

```solidity
if (amount0Removed > 0) { IERC20(ctx.token0).safeTransfer(owner, amount0Removed); }
if (amount1Removed > 0) { IERC20(ctx.token1).safeTransfer(owner, amount1Removed); }
``` [2](#0-1) 

The pool-level function signature carries no `minAmount0Out`, `minAmount1Out`, or `deadline`:

```solidity
function removeLiquidity(address owner, uint80 salt, LiquidityDelta calldata deltas, bytes calldata extensionData)
    external
    nonReentrant(PoolActions.REMOVE_LIQUIDITY)
    returns (uint256 amount0Removed, uint256 amount1Removed)
``` [3](#0-2) 

The `MetricOmmPoolLiquidityAdder` periphery contract — which does add `maxAmountToken0`/`maxAmountToken1` caps for `addLiquidity` — provides **no `removeLiquidity` wrapper at all**: [4](#0-3) 

A grep of all periphery contracts confirms zero `removeLiquidity` entry points. Users must call the pool directly, with no slippage or deadline protection available anywhere in the production surface.

---

### Impact Explanation

In Metric OMM, swaps consume liquidity from the current bin at the live oracle bid/ask price, shifting `token0BalanceScaled` and `token1BalanceScaled` inside that bin. An LP who adds to the current bin (bin 0) deposits a mix of token0 and token1 proportional to `curPosInBin`. If the oracle price moves and swaps drain most of one token from the bin before the LP's `removeLiquidity` transaction executes, the LP receives a heavily skewed composition — potentially near-zero of one token — with no on-chain protection. The total value is approximately preserved (swaps occur at oracle prices), but the LP suffers a real loss if they needed a specific token (e.g., to repay a debt, meet a collateral requirement, or satisfy a downstream obligation). There is no deadline parameter, so a pending transaction can sit in the mempool indefinitely and execute at an arbitrarily bad composition.

---

### Likelihood Explanation

Any swap that crosses the current bin between the LP's transaction submission and its inclusion changes the composition. On active pools with frequent oracle updates and swap volume, this is a routine occurrence. No privileged actor is required; normal swap activity is sufficient. The LP has no way to set a deadline or minimum output floor, so the exposure is permanent for every `removeLiquidity` call.

---

### Recommendation

1. Add `minAmount0Out` and `minAmount1Out` parameters to `MetricOmmPool.removeLiquidity()` (or enforce them in a periphery wrapper), reverting if the computed amounts fall below the caller's floor.
2. Add a `deadline` parameter (or enforce it in a periphery wrapper) to prevent stale pending transactions from executing at an unfavorable composition.
3. Alternatively, add a `removeLiquidity` function to `MetricOmmPoolLiquidityAdder` that wraps the pool call and checks both minimum outputs and deadline, mirroring the pattern already used for `addLiquidityExactShares`.

---

### Proof of Concept

1. LP calls `addLiquidity` on the current bin (bin 0) via `MetricOmmPoolLiquidityAdder`, depositing 50 token0 and 50 token1 at `curPosInBin = type(uint104).max / 2`.
2. LP submits `pool.removeLiquidity(owner, salt, deltas, "")` to recover their tokens.
3. Before the LP's tx is mined, a large swap (`zeroForOne = true`) executes at the oracle ask price, consuming nearly all token0 from bin 0. `binState.token0BalanceScaled` drops to near zero; `binState.token1BalanceScaled` increases.
4. LP's `removeLiquidity` executes:
   - `amount0Scaled = token0BalanceScaled * shares / totalShares` → ~0
   - `amount1Scaled = token1BalanceScaled * shares / totalShares` → ~100 (in scaled units)
5. LP receives ~0 token0 and ~100 token1 instead of the expected ~50/~50 split. No revert occurs; no minimum-output check exists anywhere in the call path. [5](#0-4) [3](#0-2) [4](#0-3)

### Citations

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L161-250)
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

**File:** metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol (L49-81)
```text
  // ============ External: liquidity ============

  /// @notice Add liquidity with explicit per-bin shares; reverts in callback if token amounts exceed caps.
  /// @dev `msg.sender` is always the payer for token pulls in callback (stored in transient settlement context).
  /// @param owner Position owner recorded by the pool.
  /// @param maxAmountToken0 Max token0 (native units) the pool may request; inclusive check before pull.
  /// @param maxAmountToken1 Max token1 (native units) the pool may request; inclusive check before pull.
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
