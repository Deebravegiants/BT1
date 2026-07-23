Looking at the codebase, I need to trace the deadline/timelock analog across the swap and liquidity paths.

**Key observation:** `MetricOmmSimpleRouter` correctly calls `_checkDeadline(params.deadline)` in every swap entry point, but `MetricOmmPoolLiquidityAdder` has no deadline parameter or check in any of its public functions.

---

### Title
Missing Deadline Check in `MetricOmmPoolLiquidityAdder` Allows Stale Liquidity Execution — (File: `metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol`)

### Summary
`MetricOmmPoolLiquidityAdder` exposes `addLiquidityExactShares` and `addLiquidityWeighted` without any deadline parameter or time-validity check. The swap router (`MetricOmmSimpleRouter`) correctly enforces deadlines via `_checkDeadline(params.deadline)` in all four swap entry points, but the liquidity adder has no equivalent guard. A miner or sequencer can withhold a pending liquidity transaction until the oracle price has drifted, executing it at a stale price that is adverse to the user.

### Finding Description

`MetricOmmSimpleRouter` calls `_checkDeadline` at the top of every swap function: [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

In contrast, both public entry points in `MetricOmmPoolLiquidityAdder` accept no `deadline` parameter and perform no time-based check: [5](#0-4) [6](#0-5) 

The pool's `swap` function derives bid/ask prices from a live oracle call at execution time: [7](#0-6) 

`addLiquidity` similarly uses the live oracle price to determine bin composition and share issuance. If the oracle price at execution time differs from the price at submission time, the user receives a different token composition and share count than intended.

`addLiquidityWeighted` does include a `_validateBinAndBinPosition` guard: [8](#0-7) 

However, this guard only checks whether the pool's current bin index and intra-bin cursor fall within user-supplied integer bounds. It does **not** constrain the oracle price. The oracle price can move substantially while the bin cursor remains within the user's bounds, meaning the guard does not substitute for a deadline.

`addLiquidityExactShares` has no slippage guard at all beyond the `maxAmountToken0`/`maxAmountToken1` caps, which bound only the tokens paid in — not the shares received out: [9](#0-8) 

### Impact Explanation

A miner or sequencer can observe a pending `addLiquidity` transaction in the mempool and delay its inclusion until the oracle price has moved adversely. Because there is no deadline:

- The user's token outlay is capped by `maxAmountToken0`/`maxAmountToken1`, but the LP shares received are not bounded below.
- If the oracle price drifts, the pool's bin composition changes; the user may receive significantly fewer shares for the same token cost, or add liquidity at a price that immediately creates impermanent loss relative to the current market.
- For `addLiquidityWeighted`, the probe-then-execute pattern reads oracle state at execution time. If the oracle has moved, the scaled share count and token composition will differ from what the user computed off-chain.

This constitutes a direct loss of owed LP assets (fewer shares than the user is entitled to at the price they intended to transact at), matching the allowed impact gate.

### Likelihood Explanation

Any mempool-visible transaction is subject to ordering by miners/sequencers. On chains with MEV infrastructure this is a realistic and low-cost attack. The attacker needs only to delay inclusion; no capital is required. The `addLiquidityWeighted` path is particularly exposed because it is designed for users who want to add liquidity at the current oracle price — exactly the scenario where a stale oracle price causes the greatest deviation from intent.

### Recommendation

Add a `uint256 deadline` parameter to both `addLiquidityExactShares` overloads and both `addLiquidityWeighted` overloads in `MetricOmmPoolLiquidityAdder`, and call `_checkDeadline(deadline)` at the top of each function, consistent with the pattern already used in `MetricOmmSimpleRouter`.

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

Apply the same change to `addLiquidityWeighted`.

### Proof of Concept

1. User submits `addLiquidityExactShares(pool, owner, salt, deltas, 1000e18, 500e18, "")` when oracle mid-price is `P`. Off-chain simulation shows the user will receive `S` shares.
2. Miner withholds the transaction from inclusion.
3. Oracle price moves to `P'` (e.g., token0 appreciates 10%). The pool's bin composition now requires more token0 per share.
4. Miner includes the transaction at `P'`. The pool still accepts it — `maxAmountToken0 = 1000e18` is not exceeded — but issues only `S' < S` shares because each share now represents more token0.
5. User has paid the same tokens but received fewer LP shares than intended. No revert occurs; no deadline check exists to protect them.
6. Contrast: an equivalent swap through `MetricOmmSimpleRouter.exactInputSingle` with the same submission would have reverted at step 4 via `_checkDeadline`.

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

**File:** metric-periphery/contracts/MetricOmmSimpleRouter.sol (L130-131)
```text
  function exactOutputSingle(ExactOutputSingleParams calldata params) external payable returns (uint256 amountIn) {
    _checkDeadline(params.deadline);
```

**File:** metric-periphery/contracts/MetricOmmSimpleRouter.sol (L154-155)
```text
  function exactOutput(ExactOutputParams calldata params) external payable returns (uint256 amountIn) {
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

**File:** metric-periphery/contracts/MetricOmmPoolLiquidityAdder.sol (L162-167)
```text
    (address expectedPool, address payer, uint256 max0, uint256 max1) = _loadPayContext();
    if (expectedPool == address(0)) revert CallbackContextNotActive();
    if (msg.sender != expectedPool) revert InvalidCallbackCaller(msg.sender, expectedPool);
    if (amount0Delta > max0 || amount1Delta > max1) {
      revert MaxAmountExceeded(amount0Delta, amount1Delta, max0, max1);
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

**File:** metric-core/contracts/MetricOmmPool.sol (L804-813)
```text
  function _getBidAndAskPriceX64() internal returns (uint128 bidPriceX64, uint128 askPriceX64) {
    address activePriceProvider = _resolvedPriceProvider();
    try IPriceProvider(activePriceProvider).getBidAndAskPrice() returns (uint128 bid, uint128 ask) {
      if (bid >= ask) revert BidGreaterThanAsk();
      if (bid == 0) revert BidIsZero();
      return (bid, ask);
    } catch (bytes memory reason) {
      revert PriceProviderFailed(reason);
    }
  }
```
