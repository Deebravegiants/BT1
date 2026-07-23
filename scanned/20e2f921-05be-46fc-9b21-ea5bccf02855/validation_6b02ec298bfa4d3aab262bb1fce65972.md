### Title
Missing Deadline Guard on `MetricOmmPoolLiquidityAdder` Allows Stale Liquidity Deposits at Shifted Oracle Prices - (File: metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol)

### Summary
`MetricOmmPoolLiquidityAdder` exposes four public liquidity entry points (`addLiquidityExactShares` × 2, `addLiquidityWeighted` × 2) with no `deadline` parameter and no `_checkDeadline` guard. A pending transaction can sit in the mempool and execute arbitrarily late, after the oracle price has moved significantly, deploying the user's tokens into bins at a price the user never intended to accept.

### Finding Description
`MetricOmmSimpleRouter` calls `_checkDeadline(params.deadline)` as the very first statement in every swap entry point (`exactInputSingle`, `exactInput`, `exactOutputSingle`, `exactOutput`). [1](#0-0) [2](#0-1) [3](#0-2) 

`MetricOmmPoolLiquidityAdder` has no equivalent guard on any of its entry points: [4](#0-3) [5](#0-4) 

The `addLiquidityWeighted` path is the most dangerous variant. It performs a live probe at execution time to determine the current `need0`/`need1` token ratio, then scales the user's weight vector to that ratio and pulls tokens from the user: [6](#0-5) [7](#0-6) 

The cursor-bounds check (`_validateBinAndBinPosition`) provides only coarse protection — it only reverts if the pool cursor has moved outside the caller-supplied `[minimalCurBin, maximalCurBin]` range, not if the oracle price has drifted significantly within that range: [8](#0-7) 

`addLiquidityExactShares` has no cursor-bounds check at all — it calls `_addLiquidity` directly after only validating array lengths and the owner address: [4](#0-3) 

### Impact Explanation
A user submits `addLiquidityWeighted` or `addLiquidityExactShares` when the oracle price is at level P₀. The transaction is delayed in the mempool (network congestion, low gas). The oracle price moves to P₁ (e.g., +10–20%). When the transaction finally executes:

- For `addLiquidityWeighted`: the probe runs at P₁, producing a completely different `need0`/`need1` composition. The user's tokens are pulled (up to `maxAmountToken0`/`maxAmountToken1`) and deposited into bins calibrated to P₁. If the price reverts toward P₀, the LP position immediately suffers impermanent loss relative to the price the user intended to enter at.
- For `addLiquidityExactShares`: the user's specified shares are deposited into bins that may now be deeply out-of-range relative to the live oracle price, locking capital in inactive bins with no fee accrual.

The `maxAmountToken0`/`maxAmountToken1` caps bound the nominal token outflow but do not protect against the economic loss from deploying capital at the wrong price point. The user cannot recover the difference without removing liquidity and re-entering, incurring gas and potential further slippage. [9](#0-8) 

### Likelihood Explanation
Any user who submits a liquidity transaction during periods of network congestion or gas price spikes is exposed. The `addLiquidityWeighted` variant is the primary user-facing path for LPs who do not want to compute exact shares off-chain. Mempool delays of minutes to hours are routine on Ethereum mainnet and Base during high-activity periods. No privileged access is required — any LP using the standard periphery contract is affected.

### Recommendation
Add a `deadline` parameter to all four public entry points in `MetricOmmPoolLiquidityAdder` and call `_checkDeadline(deadline)` as the first statement, mirroring the pattern already established in `MetricOmmSimpleRouter`:

```solidity
function addLiquidityExactShares(
    address pool,
    address owner,
    uint80 salt,
    LiquidityDelta calldata deltas,
    uint256 maxAmountToken0,
    uint256 maxAmountToken1,
    uint256 deadline,          // ← add
    bytes calldata extensionData
) external payable override returns (uint256 amount0Added, uint256 amount1Added) {
    _checkDeadline(deadline);  // ← add
    ...
}
```

The `_checkDeadline` helper already exists in `MetricOmmSwapRouterBase`; `MetricOmmPoolLiquidityAdder` should inherit from the same base or duplicate the one-liner.

### Proof of Concept

1. User approves `MetricOmmPoolLiquidityAdder` for up to 10,000 USDC and 5 WETH.
2. User calls `addLiquidityWeighted(pool, salt, weights, 10000e6, 5e18, -1, 0, 1, 1e18, "")` when oracle mid = $2,000/ETH.
3. Transaction is stuck in mempool for 30 minutes; oracle price moves to $2,400/ETH.
4. Transaction executes: probe runs at $2,400, `need0`/`need1` ratio reflects the new price. Scale factor is computed against the user's caps. Tokens are pulled and deposited into bins around $2,400.
5. Oracle price reverts to $2,000 within the hour. The LP position is now deeply out-of-range on the token0 side; the user has effectively bought ETH at $2,400 with their USDC leg.
6. User removes liquidity and receives fewer tokens in aggregate than they would have at their intended entry price — a direct economic loss bounded by `maxAmountToken0`/`maxAmountToken1` but not zero. [5](#0-4) [1](#0-0)

### Citations

**File:** metric-periphery/contracts/MetricOmmSimpleRouter.sol (L67-68)
```text
  function exactInputSingle(ExactInputSingleParams calldata params) external payable returns (uint256 amountOut) {
    _checkDeadline(params.deadline);
```

**File:** metric-periphery/contracts/MetricOmmSimpleRouter.sol (L92-93)
```text
  function exactInput(ExactInputParams calldata params) external payable returns (uint256 amountOut) {
    _checkDeadline(params.deadline);
```

**File:** metric-periphery/contracts/base/MetricOmmSwapRouterBase.sol (L91-94)
```text
  function _checkDeadline(uint256 deadline) internal view {
    // forge-lint: disable-next-line(block-timestamp)
    if (block.timestamp > deadline) revert IMetricOmmSimpleRouter.TransactionExpired(deadline, block.timestamp);
  }
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

**File:** metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol (L162-178)
```text
    (address expectedPool, address payer, uint256 max0, uint256 max1) = _loadPayContext();
    if (expectedPool == address(0)) revert CallbackContextNotActive();
    if (msg.sender != expectedPool) revert InvalidCallbackCaller(msg.sender, expectedPool);
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

**File:** metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol (L226-243)
```text
  function _scaleWeightsToShares(LiquidityDelta calldata w, uint256 max0, uint256 max1, uint256 need0, uint256 need1)
    internal
    pure
    returns (LiquidityDelta memory out)
  {
    uint256 scaleWad0 = need0 == 0 ? type(uint256).max : Math.mulDiv(max0, WAD, need0);
    uint256 scaleWad1 = need1 == 0 ? type(uint256).max : Math.mulDiv(max1, WAD, need1);
    uint256 scaleWad = scaleWad0 < scaleWad1 ? scaleWad0 : scaleWad1;

    uint256 n = w.binIdxs.length;
    out.binIdxs = new int256[](n);
    out.shares = new uint256[](n);
    for (uint256 i; i < n; i++) {
      out.binIdxs[i] = w.binIdxs[i];
      out.shares[i] = Math.mulDiv(w.shares[i], scaleWad, WAD);
      if (w.shares[i] != 0 && out.shares[i] == 0) revert SharesRoundedToZero();
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
