Audit Report

## Title
Swap and `addLiquidity` Permanently DoS'd; LP Principal Lost on `removeLiquidity` When USDT Transfer Fee Is Non-Zero — (File: `metric-core/contracts/MetricOmmPool.sol`, `metric-core/contracts/libraries/LiquidityLib.sol`)

## Summary
`MetricOmmPool.swap()` and `LiquidityLib.addLiquidity()` verify callback settlement using expected-amount balance checks (`balanceBefore + expectedAmount > balanceAfter`). When USDT has a non-zero transfer fee, the callback delivers `amount - fee` to the pool, causing the check to always revert. Additionally, `removeLiquidity()` silently delivers `amount - fee` to the LP while decrementing bin state by the full `amount`, causing permanent LP principal loss. USDT is explicitly in scope per the contest README.

## Finding Description

**Swap path (`zeroForOne`, token0 = USDT):**

In `MetricOmmPool.swap()`:
```solidity
uint256 balance0Before = balance0();
IMetricOmmSwapCallback(msg.sender).metricOmmSwapCallback(amount0Delta, amount1Delta, callbackData);
if (amount0Delta > 0 && balance0Before + uint256(amount0Delta) > balance0()) {
    revert IncorrectDelta();
}
``` [1](#0-0) 

`balance0()` is a plain `balanceOf` call: [2](#0-1) 

When USDT's `basisPointsRate > 0`, the callback's `transferFrom(payer, pool, amount0Delta)` causes the pool to receive only `amount0Delta - fee`. The condition `balance0Before + amount0Delta > balance0Before + amount0Delta - fee` is always `true`, so `IncorrectDelta` fires on every call.

**`addLiquidity` path:**

The identical pattern exists in `LiquidityLib.addLiquidity()`:
```solidity
uint256 balance0Before = IERC20(ctx.token0).balanceOf(address(this));
IMetricOmmModifyLiquidityCallback(msg.sender)
    .metricOmmModifyLiquidityCallback(amount0Added, amount1Added, callbackData);
if (amount0Added > 0 && balance0Before + amount0Added > IERC20(ctx.token0).balanceOf(address(this))) {
    revert IMetricOmmPoolActions.InsufficientTokenBalance();
}
``` [3](#0-2) 

**`removeLiquidity` path:**

`removeLiquidity` decrements bin state by `amount0Removed` then calls `safeTransfer(owner, amount0Removed)`: [4](#0-3) 

USDT deducts its fee from the transfer, so the LP receives `amount0Removed - fee` while the pool's bin accounting was already reduced by the full `amount0Removed`. The fee amount is stranded in the pool's raw balance, unrecoverable by the LP.

## Impact Explanation

Any pool with USDT as token0 or token1 with a non-zero fee becomes completely non-functional for swaps (`IncorrectDelta` revert) and liquidity additions (`InsufficientTokenBalance` revert). `removeLiquidity` succeeds but LPs receive `amount - fee` instead of `amount`, constituting direct loss of LP principal on every withdrawal. This satisfies "Broken core pool functionality causing loss of funds" and "direct loss of user principal" within the allowed impact gate. Severity is High: direct LP principal loss with no constraint other than USDT's fee being enabled.

## Likelihood Explanation

USDT is explicitly in scope per the contest README: "USDC and USDT should be considered in scope." [5](#0-4) 

USDT's `basisPointsRate` is currently 0 on mainnet but the setter is live and callable by Tether's owner at any time. No attacker action is required — any ordinary swap or liquidity call triggers the breakage immediately once the fee is enabled. Pools pairing USDT are a natural deployment target given the protocol's stated scope.

## Recommendation

Replace expected-amount checks with actual-received-delta checks in both `MetricOmmPool.swap()` and `LiquidityLib.addLiquidity()`:

```solidity
// swap, zeroForOne branch
uint256 balance0Before = balance0();
IMetricOmmSwapCallback(msg.sender).metricOmmSwapCallback(amount0Delta, amount1Delta, callbackData);
uint256 actualReceived = balance0() - balance0Before;
if (amount0Delta > 0 && actualReceived < uint256(amount0Delta)) {
    revert IncorrectDelta();
}
```

Apply the same pattern in `LiquidityLib.addLiquidity()`. For `removeLiquidity()`, either measure the actual balance decrease and credit only that to the LP, or document that fee-on-transfer tokens are unsupported and gate pool creation accordingly.

## Proof of Concept

1. Deploy a pool with USDT as `token0` and any standard ERC20 as `token1`.
2. Seed the pool with liquidity via direct token transfer (bypassing `addLiquidity`).
3. Enable USDT's fee: `usdt.setParams(10, 100)` (10 bps, max 100 USDT).
4. Call `pool.swap(recipient, true, 10_000e6, 0, callbackData, "")` — `zeroForOne`, selling USDT.
5. Router callback executes `usdt.transferFrom(payer, pool, amount0Delta)`.
6. USDT deducts its fee; pool receives `amount0Delta - fee`.
7. `balance0Before + amount0Delta > balance0()` → `true` → `IncorrectDelta` revert.
8. Repeat for `addLiquidity` — same revert path via `InsufficientTokenBalance`.
9. Call `removeLiquidity` — succeeds, but LP wallet receives `amount0Removed - fee`; the shortfall is permanently stranded in the pool's raw balance and unrecoverable.

### Citations

**File:** metric-core/contracts/MetricOmmPool.sol (L257-263)
```text
      uint256 balance0Before = balance0();
      IMetricOmmSwapCallback(msg.sender).metricOmmSwapCallback(amount0Delta, amount1Delta, callbackData);
      // casting to uint256 is safe because amount0Delta is positive and the ammount of tokens in pool is capped by uint128.max
      // forge-lint: disable-next-line(unsafe-typecast)
      if (amount0Delta > 0 && balance0Before + uint256(amount0Delta) > balance0()) {
        revert IncorrectDelta();
      }
```

**File:** metric-core/contracts/MetricOmmPool.sol (L556-558)
```text
  function balance0() internal view returns (uint256) {
    return IERC20(TOKEN0).balanceOf(address(this));
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

**File:** README.md (L16-16)
```markdown
Standard: ERC-20 only. USDC and USDT should be considered in scope. If the users create a pool with non-standard ERC20 tokens, the issues related to these are out of scope
```
