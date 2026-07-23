### Title
Missing Expiration Deadline in `MetricOmmPoolLiquidityAdder` Allows Miner-Delayed Execution at Stale Oracle Price - (File: metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol)

### Summary

`MetricOmmPoolLiquidityAdder` exposes `addLiquidityExactShares` and `addLiquidityWeighted` with no `deadline` parameter. A malicious validator can hold the transaction in the mempool until the oracle price has moved to a point that is unfavorable for the LP, then include it, causing the LP to deposit at a stale price and suffer immediate impermanent loss.

### Finding Description

`MetricOmmSimpleRouter` correctly guards every swap entry-point with `_checkDeadline(params.deadline)`: [1](#0-0) 

All four router functions call it: [2](#0-1) [3](#0-2) 

`MetricOmmPoolLiquidityAdder`, however, has no `deadline` parameter in any of its public entry-points: [4](#0-3) [5](#0-4) 

The `addLiquidityWeighted` overloads accept `minimalCurBin`/`maximalCurBin` cursor bounds, which provide partial protection against price movement, but:
- They are optional (callers routinely pass `type(int8).min` / `type(int8).max` to disable them).
- They check the bin index, not the oracle price itself.
- `addLiquidityExactShares` has no cursor bounds at all. [6](#0-5) 

### Impact Explanation

Because Metric OMM is oracle-anchored, the pool's bid/ask and cursor position track the external price feed. If a validator withholds the `addLiquidity*` transaction until the oracle price has moved significantly:

1. The LP's intended deposit ratio (e.g., 50/50 at price P) is executed at a new price P′.
2. The pool immediately prices the LP's position at P′, so the position is worth less than the tokens deposited.
3. Arbitrageurs can extract the difference in the same block.

The `maxAmountToken0`/`maxAmountToken1` caps bound the absolute token pull but do not prevent the ratio mismatch that causes the loss. [7](#0-6) 

### Likelihood Explanation

Any block proposer who sees the pending `addLiquidity*` transaction can delay inclusion until the oracle price moves in a direction that maximises the LP's impermanent loss. No special privilege is required beyond normal validator capabilities. The attack is more likely on chains with longer block times or during periods of high oracle volatility.

### Recommendation

Add a `uint256 deadline` parameter to all `addLiquidityExactShares` and `addLiquidityWeighted` overloads and validate it at entry using the same pattern already present in `MetricOmmSwapRouterBase._checkDeadline`:

```solidity
// forge-lint: disable-next-line(block-timestamp)
if (block.timestamp > deadline) revert TransactionExpired(deadline, block.timestamp);
``` [1](#0-0) 

### Proof of Concept

1. LP submits `addLiquidityExactShares(pool, salt, deltas, max0, max1, "")` targeting a 50/50 deposit at oracle price P.
2. Validator withholds the transaction. Oracle price moves from P to P′ (e.g., +10%).
3. Validator includes the transaction. The pool cursor has advanced; the LP's shares now require a token ratio matching P′.
4. LP receives shares priced at P′ but paid tokens at the P ratio — the position is immediately worth less than deposited.
5. An arbitrageur swaps against the pool in the same block, extracting the difference.

No deadline check exists to revert the transaction when the price has moved beyond the LP's tolerance. [8](#0-7) [9](#0-8)

### Citations

**File:** metric-periphery/contracts/base/MetricOmmSwapRouterBase.sol (L91-94)
```text
  function _checkDeadline(uint256 deadline) internal view {
    // forge-lint: disable-next-line(block-timestamp)
    if (block.timestamp > deadline) revert IMetricOmmSimpleRouter.TransactionExpired(deadline, block.timestamp);
  }
```

**File:** metric-periphery/contracts/MetricOmmSimpleRouter.sol (L67-68)
```text
  function exactInputSingle(ExactInputSingleParams calldata params) external payable returns (uint256 amountOut) {
    _checkDeadline(params.deadline);
```

**File:** metric-periphery/contracts/MetricOmmSimpleRouter.sol (L130-131)
```text
  function exactOutputSingle(ExactOutputSingleParams calldata params) external payable returns (uint256 amountIn) {
    _checkDeadline(params.deadline);
```

**File:** metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol (L56-68)
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
```

**File:** metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol (L88-116)
```text
  function addLiquidityWeighted(
    address pool,
    address owner,
    uint80 salt,
    LiquidityDelta calldata weightDeltas,
    uint256 maxAmountToken0,
    uint256 maxAmountToken1,
    int8 minimalCurBin,
    uint104 minimalPosition,
    int8 maximalCurBin,
    uint104 maximalPosition,
    bytes calldata extensionData
  ) external payable override returns (uint256 amount0Added, uint256 amount1Added) {
    _validateOwner(owner);
    _validateDeltas(weightDeltas);
    _validatePositiveWeights(weightDeltas);
    _validateBinAndBinPosition(pool, minimalCurBin, minimalPosition, maximalCurBin, maximalPosition);

    try IMetricOmmPoolActions(pool)
      .addLiquidity(owner, salt, weightDeltas, abi.encode(KIND_PROBE), extensionData) returns (
      uint256, uint256
    ) {
      revert WeightedProbeInconclusive();
    } catch (bytes memory reason) {
      (uint256 need0, uint256 need1) = _decodeLiquidityProbeOrBubble(reason);
      LiquidityDelta memory scaled = _scaleWeightsToShares(weightDeltas, maxAmountToken0, maxAmountToken1, need0, need1);
      return _addLiquidity(pool, owner, salt, scaled, msg.sender, maxAmountToken0, maxAmountToken1, extensionData);
    }
  }
```

**File:** metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol (L165-178)
```text
    if (amount0Delta > max0 || amount1Delta > max1) {
      revert MaxAmountExceeded(amount0Delta, amount1Delta, max0, max1);
    }

    PoolImmutables memory imm = IMetricOmmPool(msg.sender).getImmutables();
    address token0 = imm.token0;
    address token1 = imm.token1;
    if (amount0Delta > 0) {
      pay(token0, payer, msg.sender, amount0Delta);
    }
    if (amount1Delta > 0) {
      pay(token1, payer, msg.sender, amount1Delta);
    }
    _clearPayContext();
```

**File:** metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol (L183-207)
```text
  function _addLiquidity(
    address pool,
    address positionOwner,
    uint80 salt,
    LiquidityDelta memory deltas,
    address payer,
    uint256 maxAmountToken0,
    uint256 maxAmountToken1,
    bytes calldata extensionData
  ) internal returns (uint256 amount0Added, uint256 amount1Added) {
    _setPayContext(pool, payer, maxAmountToken0, maxAmountToken1);
    try IMetricOmmPoolActions(pool)
      .addLiquidity(positionOwner, salt, deltas, abi.encode(KIND_PAY), extensionData) returns (
      uint256 a0, uint256 a1
    ) {
      amount0Added = a0;
      amount1Added = a1;
      _clearPayContext();
    } catch (bytes memory reason) {
      _clearPayContext();
      assembly ("memory-safe") {
        revert(add(reason, 32), mload(reason))
      }
    }
  }
```

**File:** metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol (L263-286)
```text
  function _validateBinAndBinPosition(
    address pool,
    int8 minimalCurBin,
    uint104 minimalPosition,
    int8 maximalCurBin,
    uint104 maximalPosition
  ) internal view {
    if (minimalCurBin > maximalCurBin) {
      revert CursorOutOfBounds(0, 0, minimalCurBin, minimalPosition, maximalCurBin, maximalPosition);
    }

    (, int8 curBinIdx, uint104 curPosInBin,,,) = PoolStateLibrary._slot0(pool);

    int256 curBin = curBinIdx;
    if (curBin < minimalCurBin || curBin > maximalCurBin) {
      revert CursorOutOfBounds(curBinIdx, curPosInBin, minimalCurBin, minimalPosition, maximalCurBin, maximalPosition);
    }
    if (curBinIdx == minimalCurBin && curPosInBin < minimalPosition) {
      revert CursorOutOfBounds(curBinIdx, curPosInBin, minimalCurBin, minimalPosition, maximalCurBin, maximalPosition);
    }
    if (curBinIdx == maximalCurBin && curPosInBin > maximalPosition) {
      revert CursorOutOfBounds(curBinIdx, curPosInBin, minimalCurBin, minimalPosition, maximalCurBin, maximalPosition);
    }
  }
```
