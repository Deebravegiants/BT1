### Title
Missing Slippage Protection in `addLiquidity` and `removeLiquidity` Exposes LPs to Front-Running Loss — (File: metric-core/contracts/libraries/LiquidityLib.sol)

---

### Summary

`LiquidityLib.addLiquidity` and `LiquidityLib.removeLiquidity` compute required/returned token amounts entirely from live bin state at execution time, but neither function exposes a `maxAmount0`/`maxAmount1` cap or a `minAmount0Out`/`minAmount1Out` floor. Any swap that settles between an LP's transaction submission and its on-chain execution can silently shift the amounts the LP pays or receives, enabling a front-running attack that causes direct, measurable loss of user principal.

---

### Finding Description

**`addLiquidity` — unbounded token cost**

The LP supplies only a `shares` quantity per bin. The pool then computes the required token amounts from live state:

For bins that already hold shares: [1](#0-0) 

For the active bin when it is empty (first depositor), the split depends on `curPosInBin`, which advances with every swap: [2](#0-1) 

The computed totals are then handed directly to the callback with no upper bound: [3](#0-2) 

The `addLiquidity` signature at the pool level accepts no `maxAmount0` / `maxAmount1` parameter: [4](#0-3) 

**`removeLiquidity` — unbounded token receipt**

Returned amounts are computed proportionally from live bin balances: [5](#0-4) 

Tokens are transferred directly to `owner` with no `minAmount0Out` / `minAmount1Out` floor: [6](#0-5) 

The pool-level `removeLiquidity` signature likewise carries no slippage guard: [7](#0-6) 

**Critically, `addLiquidity` and `removeLiquidity` are intentionally not gated by `whenNotPaused`**, meaning they remain live even when swaps are paused, and the interface explicitly documents this divergence: [8](#0-7) 

This means a griefing attacker can execute a swap (when unpaused) immediately before an LP's pending `addLiquidity` or `removeLiquidity` transaction, altering `token0BalanceScaled`, `token1BalanceScaled`, and `curPosInBin` in the targeted bin(s) before the LP's call lands.

---

### Impact Explanation

- **`addLiquidity`**: After a front-running swap shifts bin balances, the LP's callback is invoked with a larger-than-anticipated `amount0Added` or `amount1Added`. If the LP's callback contract holds a pre-approved balance (the normal pattern for a liquidity router), it silently pays the inflated amount. The LP receives the same number of shares but has spent more tokens — a direct loss of principal.

- **`removeLiquidity`**: After a front-running swap drains one token side of a bin, the LP receives fewer tokens per share than expected. The difference is retained in the pool and accrues to remaining LPs — a direct transfer of value away from the withdrawing LP.

Both paths represent **direct loss of user principal / owed LP assets**, satisfying the Medium-and-above impact gate.

---

### Likelihood Explanation

- No special privilege is required; any unprivileged actor with mempool visibility can execute the attack.
- The attack is profitable whenever the gas cost of the front-running swap is less than the value extracted from the LP.
- Pools with high TVL or large pending LP transactions are the most attractive targets.
- The Metric OMM pool is oracle-priced, so the attacker's swap cost is bounded by the oracle spread — but the LP's loss from a shifted bin ratio can exceed that spread when the LP is depositing/withdrawing across multiple bins or large share quantities.

---

### Recommendation

1. **`addLiquidity`**: Add `uint256 maxAmount0` and `uint256 maxAmount1` parameters. After computing `amount0Added` and `amount1Added`, revert if either exceeds the caller's stated maximum:
   ```solidity
   if (amount0Added > maxAmount0 || amount1Added > maxAmount1) revert SlippageExceeded();
   ```

2. **`removeLiquidity`**: Add `uint256 minAmount0Out` and `uint256 minAmount1Out` parameters. After computing `amount0Removed` and `amount1Removed`, revert if either falls below the caller's stated minimum:
   ```solidity
   if (amount0Removed < minAmount0Out || amount1Removed < minAmount1Out) revert SlippageExceeded();
   ```

These checks should live in `LiquidityLib` before the callback / transfer, so they protect callers regardless of whether they go through the periphery `MetricOmmPoolLiquidityAdder` or call the core pool directly.

---

### Proof of Concept

**Setup**: Pool has bin 0 with `token0BalanceScaled = 1000`, `token1BalanceScaled = 1000`, `binTotalShares = 1000`.

**Step 1 — LP submits transaction**: LP calls `addLiquidity` with `shares = 100` for bin 0, expecting to pay `~100 token0` and `~100 token1` (proportional to current bin state).

**Step 2 — Attacker front-runs**: Attacker executes a `zeroForOne` swap that moves token0 into bin 0 and drains token1 out. After the swap: `token0BalanceScaled = 1800`, `token1BalanceScaled = 200`.

**Step 3 — LP's transaction executes**:
```
amount0Scaled = ceil(1800 * 100 / 1000) = 180   // LP expected ~100
amount1Scaled = ceil(200  * 100 / 1000) = 20    // LP expected ~100
```
The callback is invoked with `amount0Added ≈ 180 token0` and `amount1Added ≈ 20 token1`. The LP pays 80 extra token0 units of value with no recourse, because no slippage guard exists to revert the transaction.

**`removeLiquidity` mirror**: The same front-run in the opposite direction causes the LP to receive 80 fewer token0 units than expected when burning shares.

### Citations

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L91-106)
```text
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
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L109-110)
```text
            amount0Scaled = Math.ceilDiv(_checkedMul(binState.token0BalanceScaled, sharesToAdd), binTotalSharesVal);
            amount1Scaled = Math.ceilDiv(_checkedMul(binState.token1BalanceScaled, sharesToAdd), binTotalSharesVal);
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L141-148)
```text
      (amount0Added, amount1Added) =
        _deltasScaledToExternal(totalToken0ToAddScaled, totalToken1ToAddScaled, ctx, Math.Rounding.Ceil);

      if (amount0Added > 0 || amount1Added > 0) {
        uint256 balance0Before = IERC20(ctx.token0).balanceOf(address(this));
        uint256 balance1Before = IERC20(ctx.token1).balanceOf(address(this));
        IMetricOmmModifyLiquidityCallback(msg.sender)
          .metricOmmModifyLiquidityCallback(amount0Added, amount1Added, callbackData);
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L205-206)
```text
          uint256 amount0Scaled = _checkedMul(binState.token0BalanceScaled, sharesToRemove) / binTotalSharesVal;
          uint256 amount1Scaled = _checkedMul(binState.token1BalanceScaled, sharesToRemove) / binTotalSharesVal;
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L239-246)
```text
      (amount0Removed, amount1Removed) =
        _deltasScaledToExternal(totalToken0ToRemoveScaled, totalToken1ToRemoveScaled, ctx, Math.Rounding.Floor);

      if (amount0Removed > 0) {
        IERC20(ctx.token0).safeTransfer(owner, amount0Removed);
      }
      if (amount1Removed > 0) {
        IERC20(ctx.token1).safeTransfer(owner, amount1Removed);
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

**File:** metric-core/contracts/interfaces/IMetricOmmPool/IMetricOmmPoolActions.sol (L8-8)
```text
/// @dev State reads live on the concrete pool or libraries. Liquidity paths use native ERC20 amounts in callbacks; bin events carry scaled balances (`BinBalanceDelta`, see `PoolOperation.sol`). Successful `swap` consults the live price provider and is blocked when `pauseLevel != 0` (`PoolPaused`); `addLiquidity` / `removeLiquidity` are not gated by pause so ops policy can diverge (e.g. unwind while swaps are off).
```
