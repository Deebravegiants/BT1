### Title
Notional Fee Double-Counted in `collectFees` Drains LP Principal When Both Spread and Notional Fees Are Active — (File: `metric-core/contracts/MetricOmmPool.sol`)

---

### Summary

When both spread fees and notional fees are configured, `collectFees` distributes the entire token surplus (which already contains accumulated notional fees) as spread fees, and then also distributes the `notionalFeeToken0Scaled`/`notionalFeeToken1Scaled` accumulators as a second, separate notional payout. The notional fee is counted twice, causing the pool to transfer LP principal to fee recipients. The protocol's own test suite explicitly asserts this overallocation.

---

### Finding Description

**Analog classification:** The external `sysAdminCount` bug inflates a counter by granting a role to an address that already holds it, then decrements it once on revoke — leaving the counter overstated relative to reality. The Metric OMM analog is: the notional fee is "granted" to two separate accounting buckets simultaneously (the pool balance surplus and the `notionalFeeToken0Scaled` accumulator), and `collectFees` pays out both buckets independently, double-spending the same tokens.

**Swap-time notional fee accounting (exact-in, zeroForOne path):** [1](#0-0) 

After the swap math runs, `binTotals.scaledToken1` is decremented by the full `|amount1DeltaScaled|` (the tokens leaving the pool). Then the notional fee is computed and added back to `amount1DeltaScaled` (user receives less token1), while `notionalFeeToken1Scaled` is incremented: [2](#0-1) 

Result: the notional fee amount stays in the pool's token1 balance but is **not** in `binTotals.scaledToken1`. Therefore:

```
surplus1Scaled = balance1 * TOKEN_1_SCALE_MULTIPLIER - binTotals.scaledToken1
              = (spread_protocol_fees + notional_fees)   ← notional already here
```

**`collectFees` double-pays:** [3](#0-2) 

Because `spreadSumE6 = adminSpreadFeeE6_ + protocolSpreadFeeE6_`, the spread fee fractions sum to exactly `surplus0Scaled` (the entire surplus). Then the notional accumulator is paid out on top:

```
total_payout = surplus0Scaled + notionalFee0AmountScaled
             = (spread_fees + notional_fees) + notional_fees
```

The notional fee is paid out **twice**.

**The protocol's own test documents this:** [4](#0-3) 

```solidity
assertGt(total0Attempted, surplus0Scaled, "token0 attempted payout exceeds computed surplus");
assertGt(total1Attempted, surplus1Scaled, "token1 attempted payout exceeds computed surplus");
```

The `BinTotals` struct confirms that `scaledToken0`/`scaledToken1` are the only bin-level totals tracked — there is no separate notional-fee exclusion field: [5](#0-4) 

---

### Impact Explanation

Every call to `collectFees` when both spread and notional fees are non-zero transfers `notionalFeeToken0Scaled + notionalFeeToken1Scaled` more tokens than the actual fee surplus. These excess tokens come directly from LP principal held in `binState.token0BalanceScaled` / `binState.token1BalanceScaled`. After collection, `binTotals` overstates the pool's actual token holdings, making the pool insolvent: LP claims backed by `binTotals` cannot be fully honoured on `removeLiquidity`.

---

### Likelihood Explanation

Requires both spread fees (`spreadFeeE6 > 0`) and notional fees (`notionalFeeE8 > 0`) to be configured simultaneously — a standard production configuration explicitly tested by the protocol. Every `collectFees` call in this state triggers the overallocation. The magnitude scales with swap volume (larger notional accumulator → larger drain per collection).

---

### Recommendation

Exclude the notional fee accumulators from the surplus before computing spread fees:

```solidity
uint256 surplus0Scaled = (balance0 * TOKEN_0_SCALE_MULTIPLIER - binTotals.scaledToken0)
                         - notionalFeeToken0Scaled;
uint256 surplus1Scaled = (balance1 * TOKEN_1_SCALE_MULTIPLIER - binTotals.scaledToken1)
                         - notionalFeeToken1Scaled;
```

This ensures spread fees are computed only on the protocol-spread portion of the surplus, and notional fees are paid out separately from their own accumulator without overlap.

---

### Proof of Concept

1. Deploy a pool with `spreadFeeE6 = 500_000` (50%) and `notionalFeeE8 = 1_000_000` (1%).
2. Add liquidity across several bins.
3. Execute multiple swaps; both `binTotals` and `notionalFeeToken0Scaled` accumulate.
4. Call `collectFees` with non-zero spread and notional rates.
5. Observe that the pool transfers `notionalFeeToken0Scaled` more token0 than the actual spread-fee surplus, confirmed by the existing assertion in `test_collectProtocolFees_math_overallocates_whenSpreadAndNotionalBothActive`: [6](#0-5) 

After collection, verify that `IERC20(token0).balanceOf(pool) * TOKEN_0_SCALE_MULTIPLIER < binTotals.scaledToken0`, confirming pool insolvency: the pool can no longer cover all LP withdrawal claims.

### Citations

**File:** metric-core/contracts/MetricOmmPool.sol (L391-409)
```text
      uint256 spreadFee0ToAdminScaled = spreadSumE6 == 0 ? 0 : (surplus0Scaled * adminSpreadFeeE6_) / spreadSumE6;
      uint256 spreadFee1ToAdminScaled = spreadSumE6 == 0 ? 0 : (surplus1Scaled * adminSpreadFeeE6_) / spreadSumE6;

      uint256 spreadFee0ToProtocolScaled = spreadSumE6 == 0 ? 0 : (surplus0Scaled * protocolSpreadFeeE6_) / spreadSumE6;
      uint256 spreadFee1ToProtocolScaled = spreadSumE6 == 0 ? 0 : (surplus1Scaled * protocolSpreadFeeE6_) / spreadSumE6;

      uint256 notionalFee0ToAdminScaled =
        notionalSumE8 == 0 ? 0 : (notionalFee0AmountScaled * adminNotionalFeeE8_) / notionalSumE8;
      uint256 notionalFee1ToAdminScaled =
        notionalSumE8 == 0 ? 0 : (notionalFee1AmountScaled * adminNotionalFeeE8_) / notionalSumE8;

      uint256 notionalFee0ToProtocolScaled = notionalFee0AmountScaled - notionalFee0ToAdminScaled;
      uint256 notionalFee1ToProtocolScaled = notionalFee1AmountScaled - notionalFee1ToAdminScaled;

      uint256 totalFee0ToAdminScaled = spreadFee0ToAdminScaled + notionalFee0ToAdminScaled;
      uint256 totalFee1ToAdminScaled = spreadFee1ToAdminScaled + notionalFee1ToAdminScaled;

      uint256 totalFee0ToProtocolScaled = spreadFee0ToProtocolScaled + notionalFee0ToProtocolScaled;
      uint256 totalFee1ToProtocolScaled = spreadFee1ToProtocolScaled + notionalFee1ToProtocolScaled;
```

**File:** metric-core/contracts/MetricOmmPool.sol (L732-739)
```text
      if (zeroForOne) {
        // casting to uint256 is safe because amount0DeltaScaled is positive in zeroForOne flow.
        // forge-lint: disable-next-line(unsafe-typecast)
        binTotals.scaledToken0 =
          (uint256(binTotals.scaledToken0) + uint256(amount0DeltaScaled) - protocolFeeScaled).toUint128(); // forge-lint: disable-line(unsafe-typecast)
        // casting to uint128/uint256 is safe because bin totals remain bounded by uint128-scaled accounting invariants.
        // forge-lint: disable-next-line(unsafe-typecast)
        binTotals.scaledToken1 = uint128(uint256(binTotals.scaledToken1) - uint256(-amount1DeltaScaled));
```

**File:** metric-core/contracts/MetricOmmPool.sol (L756-762)
```text
            uint256 notionalFeeScaled = uint256(-amount1DeltaScaled) * notionalFeeE8 / 1e8;
            if (notionalFeeScaled > 0) {
              // safe because notionalFeeScaled is bounded by uint128
              // forge-lint: disable-next-line(unsafe-typecast)
              amount1DeltaScaled = amount1DeltaScaled + int256(notionalFeeScaled);
              notionalFeeToken1Scaled = (uint256(notionalFeeToken1Scaled) + notionalFeeScaled).toUint128();
            }
```

**File:** metric-core/test/MetricOmmPool.notionalFee.t.sol (L211-266)
```text
  function test_collectProtocolFees_math_overallocates_whenSpreadAndNotionalBothActive() public {
    pool.collectFees(PROTOCOL_FEE, ADMIN_FEE, 0, 0, adminFeeDestination);
    poolFeeConfig[address(pool)] = PoolFeeConfig({
      protocolSpreadFeeE6: PROTOCOL_FEE,
      adminSpreadFeeE6: ADMIN_FEE,
      protocolNotionalFeeE8: FEE_1_PCT_E8,
      adminNotionalFeeE8: 0
    });
    pool.setPoolFees(PROTOCOL_FEE + ADMIN_FEE, FEE_1_PCT_E8);

    _addLiquidity(1, -5, 4, 100_000, 0);
    for (uint256 i = 0; i < 8; i++) {
      _swap(0, users[0], false, int128(50_000), type(uint128).max);
      _swap(0, users[0], true, int128(10_000), 0);
    }

    (uint128 totalScaledToken0InBins, uint128 totalScaledToken1InBins) = PoolStateLibrary._slot1(_poolAddr());
    (uint128 notional0, uint128 notional1) = PoolStateLibrary._slot2(_poolAddr());
    assertGt(uint256(notional0) + uint256(notional1), 10, "notional accumulators should be non-zero");

    address adminAddr = IMetricOmmPoolFactory(factory).poolAdmin(_poolAddr());
    (uint24 protocolSpreadFeeE6, uint24 adminSpreadFeeE6,,) = IMetricOmmPoolFactory(factory).poolFeeConfig(_poolAddr());
    assertEq(adminAddr, admin);
    PoolFeeConfig memory feeConfig = poolFeeConfig[address(pool)];
    uint24 protocolNotionalFeeE8 = feeConfig.protocolNotionalFeeE8;
    uint24 adminNotionalFeeE8 = feeConfig.adminNotionalFeeE8;

    uint24 spreadFeeE6 = protocolSpreadFeeE6 + adminSpreadFeeE6;
    uint24 notionalFeeE8 = protocolNotionalFeeE8 + adminNotionalFeeE8;

    PoolImmutables memory immutables = IMetricOmmPool(address(pool)).getImmutables();
    address token0Addr = immutables.token0;
    address token1Addr = immutables.token1;
    uint256 token0Mul = immutables.token0ScaleMultiplier;
    uint256 token1Mul = immutables.token1ScaleMultiplier;

    uint256 surplus0Scaled = (MockERC20(token0Addr).balanceOf(address(pool)) * token0Mul) - totalScaledToken0InBins;
    uint256 surplus1Scaled = (MockERC20(token1Addr).balanceOf(address(pool)) * token1Mul) - totalScaledToken1InBins;

    // Mirror collect fee-split math for scaled amounts (rates passed into collectFees).
    uint256 spread0ToAdmin = spreadFeeE6 == 0 ? 0 : (surplus0Scaled * adminSpreadFeeE6) / spreadFeeE6;
    uint256 spread1ToAdmin = spreadFeeE6 == 0 ? 0 : (surplus1Scaled * adminSpreadFeeE6) / spreadFeeE6;
    uint256 spread0ToProtocol = spreadFeeE6 == 0 ? 0 : (surplus0Scaled * protocolSpreadFeeE6) / spreadFeeE6;
    uint256 spread1ToProtocol = spreadFeeE6 == 0 ? 0 : (surplus1Scaled * protocolSpreadFeeE6) / spreadFeeE6;

    uint256 notional0ToAdmin = notionalFeeE8 == 0 ? 0 : (uint256(notional0) * adminNotionalFeeE8) / notionalFeeE8;
    uint256 notional1ToAdmin = notionalFeeE8 == 0 ? 0 : (uint256(notional1) * adminNotionalFeeE8) / notionalFeeE8;
    uint256 notional0ToProtocol = uint256(notional0) - notional0ToAdmin;
    uint256 notional1ToProtocol = uint256(notional1) - notional1ToAdmin;

    uint256 total0Attempted = spread0ToAdmin + spread0ToProtocol + notional0ToAdmin + notional0ToProtocol;
    uint256 total1Attempted = spread1ToAdmin + spread1ToProtocol + notional1ToAdmin + notional1ToProtocol;

    assertGt(total0Attempted, surplus0Scaled, "token0 attempted payout exceeds computed surplus");
    assertGt(total1Attempted, surplus1Scaled, "token1 attempted payout exceeds computed surplus");
  }
```

**File:** metric-core/contracts/types/PoolStorage.sol (L4-11)
```text
/// @notice Packed bin-level totals occupying a single storage slot.
/// @dev Layout must stay `uint128, uint128` so the slot packing matches `PoolStateLibrary` EXTSLOAD decoding.
/// @param scaledToken0 Sum of `token0BalanceScaled` across all bins.
/// @param scaledToken1 Sum of `token1BalanceScaled` across all bins.
struct BinTotals {
  uint128 scaledToken0;
  uint128 scaledToken1;
}
```
