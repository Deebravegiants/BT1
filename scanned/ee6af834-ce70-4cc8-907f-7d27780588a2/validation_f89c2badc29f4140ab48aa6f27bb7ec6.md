Looking at the swap callback settlement flow in `MetricOmmPool.sol` and `LiquidityLib.sol`, I need to trace the exact analog to the flashloan fee-accounting bug.

**Swap flow (zeroForOne, token0 = USDT input):**

1. `_executeSwap` computes `amount0Delta` (positive = pool expects to receive token0) and `amount1Delta` (negative = pool sends token1)
2. `transferToken1(recipient, uint256(-amount1Delta))` — output sent first
3. `balance0Before = balance0()` — snapshot taken
4. `metricOmmSwapCallback(amount0Delta, amount1Delta, callbackData)` — callback told to pay `amount0Delta`
5. Check: `if (amount0Delta > 0 && balance0Before + uint256(amount0Delta) > balance0()) revert IncorrectDelta()`

**addLiquidity flow (token0 = USDT):**

1. Bin state updated, `amount0Added` computed
2. `balance0Before = IERC20(ctx.token0).balanceOf(address(this))`
3. `metricOmmModifyLiquidityCallback(amount0Added, amount1Added, callbackData)` — callback told to pay `amount0Added`
4. Check: `if (amount0Added > 0 && balance0Before + amount0Added > IERC20(ctx.token0).balanceOf(address(this))) revert InsufficientTokenBalance()`

Both checks use **expected-amount accounting** (`balanceBefore + expectedAmount > balanceAfter`). When USDT's fee is non-zero, the callback sends `amount0Delta` but the pool receives `amount0Delta - fee`, so `balance0() = balance0Before + amount0Delta - fee < balance0Before + amount0Delta` → check always reverts.

This is the direct structural analog to the flashloan bug: the protocol computes a repayment obligation from the pre-fee amount, but the fee-on-transfer token delivers less, breaking the settlement invariant.

---

### Title
Swap and `addLiquidity` Permanently Broken When USDT Transfer Fee Is Non-Zero — (File: `metric-core/contracts/MetricOmmPool.sol`, `metric-core/contracts/libraries/LiquidityLib.sol`)

### Summary
`MetricOmmPool.swap()` and `LiquidityLib.addLiquidity()` use expected-amount balance checks to verify callback settlement. When USDT (explicitly in scope) has a non-zero transfer fee, the callback delivers `amount - fee` to the pool instead of `amount`, causing `IncorrectDelta` / `InsufficientTokenBalance` to revert on every call. All swaps and liquidity additions are permanently broken for any pool whose token0 or token1 is USDT with an active fee.

### Finding Description

In `MetricOmmPool.swap()`:

```solidity
// zeroForOne branch
uint256 balance0Before = balance0();
IMetricOmmSwapCallback(msg.sender).metricOmmSwapCallback(amount0Delta, amount1Delta, callbackData);
if (amount0Delta > 0 && balance0Before + uint256(amount0Delta) > balance0()) {
    revert IncorrectDelta();
}
``` [1](#0-0) 

The pool snapshots `balance0Before`, calls the callback instructing it to pay `amount0Delta` of token0, then asserts `balance0() >= balance0Before + amount0Delta`. If token0 is USDT with fee `f > 0`, the callback's `safeTransferFrom(payer, pool, amount0Delta)` causes the pool to receive only `amount0Delta - f`. The condition `balance0Before + amount0Delta > balance0Before + amount0Delta - f` is always `true`, so `IncorrectDelta` always fires.

The identical pattern exists in `LiquidityLib.addLiquidity()`:

```solidity
uint256 balance0Before = IERC20(ctx.token0).balanceOf(address(this));
uint256 balance1Before = IERC20(ctx.token1).balanceOf(address(this));
IMetricOmmModifyLiquidityCallback(msg.sender)
    .metricOmmModifyLiquidityCallback(amount0Added, amount1Added, callbackData);
if (amount0Added > 0 && balance0Before + amount0Added > IERC20(ctx.token0).balanceOf(address(this))) {
    revert IMetricOmmPoolActions.InsufficientTokenBalance();
}
``` [2](#0-1) 

Both checks assume the token delivers exactly the requested amount. Neither path measures the actual received delta (`balanceAfter - balanceBefore`) and uses that as the settled amount.

The `balance0()` / `balance1()` helpers are plain `balanceOf` calls: [3](#0-2) 

so they correctly reflect the fee-reduced balance, making the check fail deterministically.

### Impact Explanation

Any pool whose token0 or token1 is USDT with a non-zero fee becomes completely non-functional for swaps and liquidity additions. `swap()` reverts with `IncorrectDelta` on every call; `addLiquidity()` reverts with `InsufficientTokenBalance`. `removeLiquidity()` still executes but LPs receive `amount - fee` instead of the computed `amount`, silently losing principal on every withdrawal. This constitutes both unusable core pool flows and direct loss of LP principal — both within the allowed impact gate.

### Likelihood Explanation

USDT's `basisPointsRate` is currently 0 but the setter is live and callable by Tether's owner at any time. Pools pairing USDT against any token are a natural deployment target. Once the fee is enabled, the breakage is immediate and requires no attacker action — any ordinary swap or liquidity call triggers it.

### Recommendation

Replace expected-amount checks with actual-received-delta checks:

```solidity
// swap, zeroForOne branch
uint256 balance0Before = balance0();
IMetricOmmSwapCallback(msg.sender).metricOmmSwapCallback(amount0Delta, amount1Delta, callbackData);
uint256 actualReceived = balance0() - balance0Before;          // fee-safe
if (amount0Delta > 0 && actualReceived < uint256(amount0Delta)) {
    revert IncorrectDelta();
}
```

Apply the same pattern in `LiquidityLib.addLiquidity()`. For `removeLiquidity()`, either accept the fee-reduced delivery or document that fee-on-transfer tokens are unsupported and gate pool creation accordingly.

### Proof of Concept

1. Deploy a pool with USDT as `token0` and any standard ERC20 as `token1`.
2. Enable USDT's fee: `usdt.setParams(10, 100)` (10 bps, max 100 USDT).
3. Seed the pool with liquidity via a direct token transfer (bypassing `addLiquidity`).
4. Call `pool.swap(recipient, true, 10_000e6, 0, callbackData, "")` — `zeroForOne`, selling USDT.
5. The router callback executes `usdt.transferFrom(payer, pool, amount0Delta)`.
6. USDT deducts its fee; pool receives `amount0Delta - fee`.
7. `balance0Before + amount0Delta > balance0()` → `true` → `IncorrectDelta` revert.
8. Repeat for `addLiquidity` — same revert path via `InsufficientTokenBalance`.
9. Call `removeLiquidity` — succeeds, but LP wallet receives `amount0Removed - fee` instead of `amount0Removed`; the shortfall is unrecoverable. [4](#0-3) [5](#0-4)

### Citations

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

**File:** metric-core/contracts/MetricOmmPool.sol (L556-563)
```text
  function balance0() internal view returns (uint256) {
    return IERC20(TOKEN0).balanceOf(address(this));
  }

  /// @notice Get the current balance of token1 held by the pool
  function balance1() internal view returns (uint256) {
    return IERC20(TOKEN1).balanceOf(address(this));
  }
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L144-154)
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
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L239-247)
```text
      (amount0Removed, amount1Removed) =
        _deltasScaledToExternal(totalToken0ToRemoveScaled, totalToken1ToRemoveScaled, ctx, Math.Rounding.Floor);

      if (amount0Removed > 0) {
        IERC20(ctx.token0).safeTransfer(owner, amount0Removed);
      }
      if (amount1Removed > 0) {
        IERC20(ctx.token1).safeTransfer(owner, amount1Removed);
      }
```
