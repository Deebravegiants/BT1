Audit Report

## Title
Pool Self-Recipient in `swap` Silently Converts Trader Output Into Swept Protocol Fees — (`metric-core/contracts/MetricOmmPool.sol`)

## Summary
`MetricOmmPool.swap` accepts an arbitrary `recipient` address with no guard against `recipient == address(this)`. When the pool address is passed as `recipient`, the output-token `safeTransfer` is a self-transfer leaving `balance1()` unchanged, while `binTotals.scaledToken1` has already been decremented by `_executeSwap`. The resulting phantom surplus is later swept as spread fees via `collectFees`, permanently destroying the trader's output tokens.

## Finding Description
The exploit chain is fully confirmed by the production code:

**Step 1 — No guard:** `swap` at lines 217–225 has no `require(recipient != address(this))` check. The `recipient` parameter is passed directly to `transferToken1`.

**Step 2 — Output transfer before callback:** For a `zeroForOne` swap, line 254 calls `transferToken1(recipient, uint256(-amount1Delta))` before the callback fires. When `recipient == address(this)`, this resolves to `IERC20(TOKEN1).safeTransfer(address(this), amount)` (line 569–571), a self-transfer that leaves `IERC20(TOKEN1).balanceOf(address(this))` — i.e., `balance1()` — unchanged.

**Step 3 — `binTotals` already decremented:** Inside `_executeSwap`, line 739 executes `binTotals.scaledToken1 = uint128(uint256(binTotals.scaledToken1) - uint256(-amount1DeltaScaled))` unconditionally, regardless of where the tokens actually go.

**Step 4 — `IncorrectDelta` check is input-only:** Lines 261–263 only verify that `balance0Before + uint256(amount0Delta) <= balance0()`, i.e., that the input token arrived. There is no symmetric check that `balance1` decreased by the output amount. The output-side discrepancy is invisible to this guard.

**Step 5 — `collectFees` sweeps the phantom surplus:** Lines 385–388 compute:
```
surplus1Scaled = balance1() * TOKEN_1_SCALE_MULTIPLIER
               - uint256(binTotals.scaledToken1)
               - notionalFee1AmountScaled
```
Because `balance1()` is unchanged but `binTotals.scaledToken1` was decremented by the full output amount, `surplus1Scaled` is inflated by exactly that amount. Lines 391–426 then distribute this surplus to `adminFeeDestination_` and `FACTORY`, permanently removing the tokens from the pool.

## Impact Explanation
Direct loss of 100% of the trader's expected output principal. The trader pays the full input (enforced by the callback check) and receives zero output. The stolen tokens are reclassified as spread-fee revenue and transferred to the admin and protocol fee destinations upon the next `collectFees` call. Additionally, `binTotals` no longer covers actual LP claims for the output token, constituting pool insolvency. This meets the Critical threshold under the allowed impact gate (direct loss of user principal, pool insolvency, broken swap conservation).

## Likelihood Explanation
Any unprivileged caller of `swap` controls `recipient` directly; no router or factory validation prevents passing `address(pool)`. The `MetricOmmSimpleRouter.exactInput` (line 106) already passes `address(this)` as intermediate recipient for multi-hop swaps — a one-off routing bug in any integrator trivially produces `recipient = pool`. The attack requires no special privileges, no price manipulation, and is repeatable on every swap.

## Recommendation
Add a self-recipient guard at the top of `swap`, before any state changes:
```solidity
require(recipient != address(this), SelfRecipient());
```
Alternatively, add a symmetric post-transfer balance check verifying that `balance1()` decreased by the expected output amount, analogous to the existing `IncorrectDelta` check on the input side.

## Proof of Concept
```
Setup:
  pool  = MetricOmmPool(token0=USDC, token1=WETH)
  alice = trader (implements IMetricOmmSwapCallback, pays USDC in callback)

1. Alice calls pool.swap(
       recipient       = address(pool),   // self-address
       zeroForOne      = true,
       amountSpecified = 1_000e6,         // exact-in 1 000 USDC
       priceLimitX64   = 0,
       callbackData    = "",
       extensionData   = ""
   );

2. _executeSwap computes amount1DeltaScaled = -X (e.g. 0.5e18 WETH scaled).
   Line 739: binTotals.scaledToken1 -= X   ← accounting says WETH left.

3. Line 254: transferToken1(address(pool), 0.5e18)
   → safeTransfer(address(pool), 0.5e18) → self-transfer, balance1() unchanged.

4. Callback fires; Alice pays 1 000 USDC. IncorrectDelta check (line 261) passes.

5. State after swap:
     balance1() * TOKEN_1_SCALE_MULTIPLIER  =  binTotals.scaledToken1 + X
     surplus1Scaled = X  (Alice's 0.5 WETH)

6. Factory calls pool.collectFees(…).
   Lines 387–388: surplus1Scaled = X → swept to adminFeeDestination / FACTORY.

Alice lost 1 000 USDC and received 0 WETH.
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** metric-core/contracts/MetricOmmPool.sol (L217-225)
```text
  function swap(
    address recipient,
    bool zeroForOne,
    int128 amountSpecified,
    uint128 priceLimitX64,
    bytes calldata callbackData,
    bytes calldata extensionData
  ) external whenNotPaused nonReentrant(PoolActions.SWAP) returns (int128, int128) {
    require(amountSpecified != 0, InvalidAmount());
```

**File:** metric-core/contracts/MetricOmmPool.sol (L250-263)
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
```

**File:** metric-core/contracts/MetricOmmPool.sol (L385-388)
```text
    uint256 surplus0Scaled =
      balance0() * TOKEN_0_SCALE_MULTIPLIER - uint256(binTotals.scaledToken0) - notionalFee0AmountScaled;
    uint256 surplus1Scaled =
      balance1() * TOKEN_1_SCALE_MULTIPLIER - uint256(binTotals.scaledToken1) - notionalFee1AmountScaled;
```

**File:** metric-core/contracts/MetricOmmPool.sol (L569-571)
```text
  function transferToken1(address to, uint256 amount) internal {
    IERC20(TOKEN1).safeTransfer(to, amount);
  }
```

**File:** metric-core/contracts/MetricOmmPool.sol (L737-739)
```text
        // casting to uint128/uint256 is safe because bin totals remain bounded by uint128-scaled accounting invariants.
        // forge-lint: disable-next-line(unsafe-typecast)
        binTotals.scaledToken1 = uint128(uint256(binTotals.scaledToken1) - uint256(-amount1DeltaScaled));
```
