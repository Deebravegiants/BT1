### Title
Exact-output swaps silently under-deliver when pool liquidity is insufficient — `priceLimitX64` does not guard against liquidity shortfall - (File: `metric-core/contracts/MetricOmmPool.sol`, `metric-periphery/contracts/MetricOmmSimpleRouter.sol`)

---

### Summary

In `MetricOmmPool`, exact-output swap paths silently cap the delivered output to available liquidity without reverting. The `priceLimitX64` parameter only guards against price movement, not against a liquidity shortfall. The periphery router's `exactOutputSingle` checks only `amountInMaximum` (input cap), never that `actualAmountOut == params.amountOut`. A large LP can front-run by removing liquidity, causing users to receive far less than the requested output while the router silently accepts the result.

---

### Finding Description

**Root cause — silent output cap in `_swapToken0ForToken1SpecifiedOutput`:** [1](#0-0) 

```solidity
uint256 totalAvailableToken1Scaled = binTotals.scaledToken1;
if (amountOutScaled > totalAvailableToken1Scaled) {
    amountOutScaled = totalAvailableToken1Scaled;   // silently reduced, no revert
}
```

When the requested output exceeds available liquidity, `amountOutScaled` is silently reduced to whatever is available. The swap then proceeds and returns the reduced delta. The symmetric path `_swapToken1ForToken0SpecifiedOutput` achieves the same silent under-delivery by simply exhausting bins and breaking the loop without reverting.

**Pool `swap` transfers actual output, not requested output:** [2](#0-1) 

After `_executeSwap`, the pool transfers `uint256(-amount1Delta)` (or `uint256(-amount0Delta)`) — the *actual* reduced output — to the recipient. There is no assertion that `|amountDelta| == |amountSpecified|`.

**Router `exactOutputSingle` checks only `amountInMaximum`, never actual output:** [3](#0-2) 

The `exactInputSingle` path has `if (amountOut < params.amountOutMinimum) revert InsufficientOutput(...)`. The `exactOutputSingle` path has no equivalent check that `actualAmountOut == params.amountOut`. It only checks:

```solidity
if (amountIn > params.amountInMaximum) revert InputTooHigh(amountIn, params.amountInMaximum);
```

When liquidity is drained, both `amountIn` and `amountOut` shrink proportionally, so `amountIn <= amountInMaximum` still holds and the router does not revert.

**`priceLimitX64` does not protect against this:** [4](#0-3) 

`priceLimitX64` is compared against marginal bin prices along the swap path. Removing liquidity does not change the oracle-derived mid-price or the bin price boundaries — it only empties bin balances. A price limit set at the current market price will not stop a swap that terminates early due to empty bins.

---

### Impact Explanation

A user calling `exactOutputSingle(amountOut = X, amountInMaximum = Y)` expects to receive exactly `X` output tokens. If an attacker drains pool liquidity before the swap:

- The pool silently delivers `X' << X` tokens to the recipient.
- The router pays `Y' << Y` input tokens (proportionally less).
- Since `Y' <= Y`, the `InputTooHigh` guard does not trigger.
- The router returns successfully; the user has no on-chain recourse.

**Direct loss of user principal**: the user receives far fewer tokens than intended with no revert or warning. This matches the BAMM analog exactly: the slippage parameter (`priceLimitX64` / `amountInMaximum`) is the only protection, but it does not cover the liquidity-drain attack vector.

---

### Likelihood Explanation

- Any LP holding a significant share of pool liquidity can execute this attack.
- The attacker calls `removeLiquidity` in the same block (front-run), waits for the victim's swap to execute, then calls `addLiquidity` to restore position.
- Cost to attacker: gas for two liquidity operations + foregone LP fees during the window.
- No special permissions required; `removeLiquidity` is open to any position owner. [5](#0-4) 

---

### Recommendation

1. **In the pool** (`MetricOmmPool.swap`): After `_executeSwap`, when `amountSpecified < 0` (exact-output mode), assert that the actual output magnitude equals the requested magnitude:

   ```solidity
   // For zeroForOne exact-output:
   if (amountSpecified < 0 && amount1Delta != amountSpecified) revert InsufficientLiquidity();
   ```

2. **In the router** (`MetricOmmSimpleRouter.exactOutputSingle`): After the swap call, verify the actual output equals the requested output:

   ```solidity
   int128 out = MetricOmmSwapResults.extractAmountOut(params.zeroForOne, amount0Delta, amount1Delta);
   uint128 amountOut = MetricOmmSwapInputs.int128ToUint128(out);
   if (amountOut < params.amountOut) revert InsufficientOutput(amountOut, params.amountOut);
   ```

   This mirrors the existing guard already present in `exactInputSingle`. [6](#0-5) 

---

### Proof of Concept

```
Setup:
  - Pool has 100,000 token1 in liquidity (LP = Attacker, 90% share)
  - User calls exactOutputSingle(amountOut=50,000, amountInMaximum=55,000, zeroForOne=true)

Attack sequence (single block):
  1. Attacker sees user tx in mempool.
  2. Attacker calls removeLiquidity() — drains 90% of token1, leaving ~10,000 token1.
  3. User's swap executes:
       - _swapToken0ForToken1SpecifiedOutput caps amountOutScaled to ~10,000 (available)
       - Pool transfers ~10,000 token1 to user (not 50,000)
       - Pool charges proportionally less token0 input (~11,000 instead of ~55,000)
       - amountIn=11,000 < amountInMaximum=55,000 → router does NOT revert
  4. Attacker calls addLiquidity() to restore position.

Result:
  - User receives 10,000 token1 instead of 50,000 (80% shortfall)
  - Router returns successfully with no error
  - Attacker's LP position is restored; net cost is only gas
``` [7](#0-6) [8](#0-7)

### Citations

**File:** metric-core/contracts/MetricOmmPool.sol (L172-212)
```text
  }

  modifier whenNotPaused() {
    _checkNotPaused();
    _;
  }

  // ============ External: liquidity ============

  /// @inheritdoc IMetricOmmPoolActions
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

  /// @inheritdoc IMetricOmmPoolActions
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

**File:** metric-core/contracts/MetricOmmPool.sol (L244-248)
```text
    SwapMath.InternalSwapParams memory params =
      SwapMath.InternalSwapParams({midPriceX64: midPriceX64, baseFeeX64: baseFeeX64, priceLimitX64: priceLimitX64});

    (int256 amount0Delta, int256 amount1Delta, uint256 protocolFeeAmount) =
      _executeSwap(zeroForOne, amountSpecified, params);
```

**File:** metric-core/contracts/MetricOmmPool.sol (L250-278)
```text
    if (zeroForOne) {
      if (amount1Delta < 0) {
        // casting to uint256 is safe because amount1Delta is negative and the ammount of tokens in pool is capped by uint128.max
        // forge-lint: disable-next-line(unsafe-typecast)
        transferToken1(recipient, uint256(-amount1Delta));
      }

      uint256 balance0Before = balance0();
      IMetricOmmSwapCallback(msg.sender).metricOmmSwapCallback(amount0Delta, amount1Delta, callbackData);
      // casting to uint256 is safe because amount0Delta is positive and the ammount of tokens in pool is capped by uint128.max
      // forge-lint: disable-next-line(unsafe-typecast)
      if (amount0Delta > 0 && balance0Before + uint256(amount0Delta) > balance0()) {
        revert IncorrectDelta();
      }
    } else {
      if (amount0Delta < 0) {
        // casting to uint256 is safe because amount0Delta is negative and the ammount of tokens in pool is capped by uint128.max
        // forge-lint: disable-next-line(unsafe-typecast)
        transferToken0(recipient, uint256(-amount0Delta));
      }

      uint256 balance1Before = balance1();
      IMetricOmmSwapCallback(msg.sender).metricOmmSwapCallback(amount0Delta, amount1Delta, callbackData);
      // casting to uint256 is safe because amount1Delta is positive and the ammount of tokens in pool is capped by uint128.max
      // forge-lint: disable-next-line(unsafe-typecast)
      if (amount1Delta > 0 && balance1Before + uint256(amount1Delta) > balance1()) {
        revert IncorrectDelta();
      }
    }
```

**File:** metric-core/contracts/MetricOmmPool.sol (L1049-1067)
```text
        uint256 totalAvailableToken1Scaled = binTotals.scaledToken1;
        if (amountOutScaled > totalAvailableToken1Scaled) {
          amountOutScaled = totalAvailableToken1Scaled;
        }
      }

      (
        BinState memory binState,
        SwapMath.SwapState memory state,
        int256 curBinIdxCache,
        uint256 curPosInBinCache,
        int256 curBinDistE6Cache,
        uint256 lowerPriceX64,
        uint256 upperPriceX64,
        uint256 initialPriceX64
      ) = _getInitialStateForSwap(true, true, params, amountOutScaled);

      if (params.priceLimitX64 >= initialPriceX64) {
        return (0, 0, 0, 0);
```

**File:** metric-periphery/contracts/MetricOmmSimpleRouter.sol (L61-86)
```text
    revert InvalidCallbackMode(callbackMode);
  }

  // ============ External: exact input ============

  /// @inheritdoc IMetricOmmSimpleRouter
  function exactInputSingle(ExactInputSingleParams calldata params) external payable returns (uint256 amountOut) {
    _checkDeadline(params.deadline);
    uint128 priceLimitX64 = MetricOmmSwapPath.normalizePriceLimit(params.zeroForOne, params.priceLimitX64);

    _setNextCallbackContext(params.pool, CALLBACK_MODE_JUST_PAY, msg.sender, params.tokenIn);
    (int128 amount0Delta, int128 amount1Delta) = IMetricOmmPoolActions(params.pool)
      .swap(
        params.recipient,
        params.zeroForOne,
        MetricOmmSwapInputs.asAmountSpecifiedIn(params.amountIn),
        priceLimitX64,
        "",
        params.extensionData
      );
    int128 out = MetricOmmSwapResults.extractAmountOut(params.zeroForOne, amount0Delta, amount1Delta);
    amountOut = MetricOmmSwapInputs.int128ToUint128(out);
    if (amountOut < params.amountOutMinimum) revert InsufficientOutput(amountOut, params.amountOutMinimum);

    _clearExpectedCallbackPool();
  }
```
