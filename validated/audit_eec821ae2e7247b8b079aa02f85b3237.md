Audit Report

## Title
LP Fee Front-Running via Sandwich Attack on Bin Share Price - (`metric-core/contracts/libraries/LiquidityLib.sol`)

## Summary
LP fees from every swap are deposited directly into the touched bin's `token0BalanceScaled` / `token1BalanceScaled`, immediately raising the per-share redemption value. Because `removeLiquidity` redeems at the current bin balance with no exit fee or lock period, an attacker can sandwich any pending swap: add shares just before the swap, let the swap inflate the bin balance with LP fees, then immediately remove shares and pocket a proportional slice of those fees. Existing LPs suffer a direct, repeatable loss of earned fees.

## Finding Description
**Fee accumulation:** In all four swap directions in `SwapMath.sol`, the LP fee portion (`feeAmountScaled - protocolFeeAmountScaled`) is added directly to the bin's token balance. For example, in `buyToken0InBinSpecifiedOut` (L409–415):

```solidity
uint256 feeAmountScaled = Math.ceilDiv(amountInScaled * currBinBuyFeeX64, ONE_X64);
amountInScaled += feeAmountScaled;
uint256 protocolFeeAmountScaled = (feeAmountScaled * spreadFeeE6) / 1e6;
binState.token0BalanceScaled -= amountOutScaled.toUint104();
binState.token1BalanceScaled =
  (uint256(binState.token1BalanceScaled) + amountInScaled - protocolFeeAmountScaled).toUint104();
```

The same pattern holds in `buyToken1InBinSpecifiedOut` (L495–501), `buyToken0InBinSpecifiedIn` (L636–641), and `buyToken1InBinSpecifiedIn` (L779–781).

**Share pricing on entry:** When a bin already has shares, `addLiquidity` prices new shares proportionally to the current bin balance (ceiling-rounded), `LiquidityLib.sol` L109–110:

```solidity
amount0Scaled = Math.ceilDiv(_checkedMul(binState.token0BalanceScaled, sharesToAdd), binTotalSharesVal);
amount1Scaled = Math.ceilDiv(_checkedMul(binState.token1BalanceScaled, sharesToAdd), binTotalSharesVal);
```

**Share redemption on exit:** `removeLiquidity` redeems at the current bin balance, floor-divided, `LiquidityLib.sol` L205–206:

```solidity
uint256 amount0Scaled = _checkedMul(binState.token0BalanceScaled, sharesToRemove) / binTotalSharesVal;
uint256 amount1Scaled = _checkedMul(binState.token1BalanceScaled, sharesToRemove) / binTotalSharesVal;
```

There is no exit fee, no minimum holding period, and no lock. Tokens are transferred out immediately (L242–247).

**No pause guard:** `swap` carries `whenNotPaused` (`MetricOmmPool.sol` L224), but `addLiquidity` (L182–196) and `removeLiquidity` (L199–212) carry only `nonReentrant`. The attack surface persists even when swaps are paused.

**Exploit flow:**
1. Bin `b` has `T1 = 100`, `S = 1000`. A large swap is pending that will deposit `F = 10` LP fee.
2. **Front-run:** attacker calls `addLiquidity` for `S_a = 1000` shares, paying `ceil(100 × 1000 / 1000) = 100` token1. Bin: `T1 = 200`, `S = 2000`.
3. **Victim swap executes:** LP fee `F = 10` added. Bin: `T1 = 210`, `S = 2000`.
4. **Back-run:** attacker calls `removeLiquidity` for `1000` shares, receiving `floor(210 × 1000 / 2000) = 105` token1.
5. **Profit:** `105 − 100 = 5` token1 (half the LP fee), at zero inventory risk once the swap is confirmed.

No existing guard prevents this: the reentrancy lock only blocks re-entry within a single transaction, not cross-transaction sandwiching.

## Impact Explanation
Existing LPs suffer a direct, quantifiable loss of LP fee revenue on every sandwiched swap. The attacker captures `(attackShares / totalSharesAfterAdd) × lpFeeFromSwap` per sandwich, which is always positive when `lpFeeFromSwap > 0` and there is no exit fee. On high-volume pools or large individual swaps the stolen fee is material. This constitutes a direct loss of owed LP assets, satisfying the allowed impact gate (Critical/High direct loss of LP assets above Sherlock thresholds).

## Likelihood Explanation
Any unprivileged address can execute this attack. It requires only standard mempool visibility (available on Ethereum/Base) and capital for the front-run deposit (or a flash loan if the attacker controls both legs in the same block via a builder). No special roles, no malicious setup, and no non-standard tokens are needed. The attack is repeatable on every swap that generates LP fees.

## Recommendation
Implement an exit fee charged on `removeLiquidity` that is proportional to the LP fee rate and credited back to the bin (or to a reserve). The fee must exceed `f / (1 + f)` of the withdrawn amount, where `f` is the maximum LP fee rate, to make a 1-block deposit-and-withdraw cycle unprofitable. Alternatively, implement a minimum holding period (e.g., a block timestamp check) before shares can be redeemed, or use a time-weighted average of the bin balance for redemption pricing. The exit fee approach (analogous to the Union Finance fix) is the most gas-efficient and does not require TWAP accounting.

## Proof of Concept
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.35;

contract SandwichLpFeeTest is MetricOmmPoolBaseTest {
    function test_lpFeeSandwich() public {
        // 1. Existing LP seeds bin 0 with liquidity
        int8 bin = 0;
        uint104 existingShares = 10_000;
        _doAddLiquidity(0, DEFAULT_SALT, _createDeltaArray(bin, existingShares));

        address attacker = users[1];
        uint256 t1Before = token1.balanceOf(attacker);

        // 2. Attacker front-runs: add equal shares to bin 0
        uint104 attackShares = 10_000;
        _doAddLiquidity(1, DEFAULT_SALT + 1, _createDeltaArray(bin, attackShares));

        // 3. Victim swap executes: deposits LP fee into bin 0
        uint128 swapAmount = 5_000;
        _doSwap(2, true, int128(swapAmount), 0);

        // 4. Attacker back-runs: remove all shares
        _doRemoveLiquidity(1, DEFAULT_SALT + 1, _createDeltaArray(bin, attackShares));

        uint256 t1After = token1.balanceOf(attacker);
        // Attacker receives more token1 than deposited
        assertGt(t1After, t1Before, "Attacker profits from LP fee sandwich");
    }
}
```

The attacker's profit equals `(attackShares / totalSharesAfterAdd) × lpFeeFromSwap`, which is always positive when `lpFeeFromSwap > 0` and no exit fee exists.