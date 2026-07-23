### Title
`collectFees` Double-Counts Notional Fees Against Spread Surplus, Draining LP Principal — (`metric-core/contracts/MetricOmmPool.sol`)

---

### Summary

When both spread fees and notional fees are active, `collectFees` distributes the full `surplus0Scaled` (which already contains the accumulated notional fees) as the spread-fee base **and** separately distributes `notionalFeeToken0Scaled` as the notional-fee base. The notional fee amount is therefore counted twice, causing the total payout to exceed the available fee surplus and pull the shortfall directly from LP principal.

---

### Finding Description

`collectFees` computes the fee surplus as:

```
surplus0Scaled = pool_balance × token0ScaleMultiplier − binTotals.scaledToken0
```

This surplus represents **all** tokens the pool holds above LP claims — both spread-fee accumulation and notional-fee accumulation. Notional fees are also tracked in the separate accumulator `notionalFeeToken0Scaled`.

The function then distributes:

```solidity
// spread leg — uses the full surplus (which already contains notional fees)
spreadFee0ToAdminScaled    = (surplus0Scaled * adminSpreadFeeE6_)    / spreadSumE6;
spreadFee0ToProtocolScaled = (surplus0Scaled * protocolSpreadFeeE6_) / spreadSumE6;

// notional leg — uses the notional accumulator (already inside surplus0Scaled)
notionalFee0ToAdminScaled    = (notionalFee0AmountScaled * adminNotionalFeeE8_)    / notionalSumE8;
notionalFee0ToProtocolScaled = notionalFee0AmountScaled − notionalFee0ToAdminScaled;

// combined transfer
totalFee0ToAdmin    = spreadFee0ToAdminScaled    + notionalFee0ToAdminScaled;
totalFee0ToProtocol = spreadFee0ToProtocolScaled + notionalFee0ToProtocolScaled;
``` [1](#0-0) 

When `spreadSumE6 > 0` and `notionalSumE8 > 0`, the combined payout approximates:

```
totalPayout ≈ surplus0Scaled + notionalFee0AmountScaled
```

But only `surplus0Scaled` tokens are available above LP claims. The excess `notionalFee0AmountScaled` is transferred out of LP-owned bin reserves.

The protocol's own test suite explicitly documents this invariant break:

```solidity
assertGt(total0Attempted, surplus0Scaled,
    "token0 attempted payout exceeds computed surplus");
assertGt(total1Attempted, surplus1Scaled,
    "token1 attempted payout exceeds computed surplus");
``` [2](#0-1) 

The transfer succeeds (no revert) because the pool holds LP funds that cover the shortfall; the ERC-20 balance check only verifies the pool has enough tokens in total, not that the surplus is sufficient.

---

### Impact Explanation

**High.** Every call to `collectFees` when both fee types are non-zero silently transfers `notionalFee0AmountScaled / token0ScaleMultiplier` token0 (and the token1 equivalent) out of LP reserves to the admin and protocol destinations. LPs cannot recover these tokens through `removeLiquidity` because `binTotals.scaledToken0` is not reduced — the bin accounting diverges from the actual pool balance, making the pool insolvent for the drained amount.

---

### Likelihood Explanation

**Medium.** The trigger requires:
1. A pool configured with both a non-zero spread fee and a non-zero notional fee (a supported and documented configuration).
2. At least one swap to accumulate notional fees.
3. A call to `collectFees` — which the factory owner invokes routinely via `setPoolProtocolFee`.

No malicious intent is required; a well-intentioned fee adjustment triggers the drain automatically. [3](#0-2) 

---

### Recommendation

Before computing the spread-fee split, subtract the notional accumulator from the surplus so the two fee bases are disjoint:

```solidity
uint256 spreadSurplus0Scaled = surplus0Scaled > notionalFee0AmountScaled
    ? surplus0Scaled - notionalFee0AmountScaled
    : 0;
uint256 spreadSurplus1Scaled = surplus1Scaled > notionalFee1AmountScaled
    ? surplus1Scaled - notionalFee1AmountScaled
    : 0;

// then use spreadSurplus0Scaled / spreadSurplus1Scaled for the spread-fee split
```

This ensures `spreadSurplus + notionalFee ≤ surplus`, preserving LP solvency.

---

### Proof of Concept

1. Deploy a pool with `spreadFeeE6 > 0` and `notionalFeeE8 > 0`.
2. Add liquidity (e.g., 100 000 scaled units across several bins).
3. Execute several swaps in both directions to accumulate both spread surplus and notional fees in `notionalFeeToken0Scaled`.
4. Read `surplus0Scaled = pool.balanceOf(token0) × multiplier − binTotals.scaledToken0` and `notional0 = notionalFeeToken0Scaled`.
5. Call `collectFees(protocolSpread, adminSpread, protocolNotional, adminNotional, adminDest)`.
6. After the call, verify:
   - `pool.balanceOf(token0)` decreased by more than `surplus0Scaled / multiplier`.
   - `binTotals.scaledToken0` is unchanged (LP accounting intact).
   - The difference equals `notional0 / multiplier` — LP principal drained.

The existing test `test_collectProtocolFees_math_overallocates_whenSpreadAndNotionalBothActive` already asserts steps 3–6 and confirms the overallocation. [4](#0-3)

### Citations

**File:** metric-core/contracts/MetricOmmPool.sol (L391-414)
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

      (uint256 totalFee0ToAdmin, uint256 totalFee1ToAdmin) =
        deltasScaledToExternal(totalFee0ToAdminScaled, totalFee1ToAdminScaled, Math.Rounding.Floor);
      (uint256 totalFee0ToProtocol, uint256 totalFee1ToProtocol) =
        deltasScaledToExternal(totalFee0ToProtocolScaled, totalFee1ToProtocolScaled, Math.Rounding.Floor);
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

**File:** metric-core/contracts/MetricOmmPoolFactory.sol (L327-335)
```text
    PoolFeeConfig memory c = poolFeeConfig[pool];
    IMetricOmmPoolCollectFees(pool)
      .collectFees(
        c.protocolSpreadFeeE6,
        c.adminSpreadFeeE6,
        c.protocolNotionalFeeE8,
        c.adminNotionalFeeE8,
        poolAdminFeeDestination[pool]
      );
```
