### Title
`collectFees` Double-Counts Notional Fees Against LP Principal When Both Spread and Notional Fees Are Active — (`metric-core/contracts/MetricOmmPool.sol`)

---

### Summary

When both spread fees and notional fees are configured, `collectFees` computes the spread-fee payout as 100% of the pool's token surplus (which already includes accumulated notional fees), and then **also** pays out the notional fee accumulator as a separate line item. The notional fees are therefore counted twice: once inside the surplus base and once as an explicit transfer. The shortfall is silently drawn from LP bin balances, causing a direct, repeatable loss of LP principal on every `collectPoolFees` call.

---

### Finding Description

`collectFees` in `MetricOmmPool.sol` computes the surplus available for fee distribution as:

```
surplus0Scaled = balance0() * TOKEN_0_SCALE_MULTIPLIER - binTotals.scaledToken0
``` [1](#0-0) 

This surplus contains **both** accumulated LP spread fees and accumulated notional fees (which are held in the pool's ERC-20 balance but not credited to `binTotals`).

The spread-fee split is then computed as:

```solidity
spreadFee0ToAdminScaled    = (surplus0Scaled * adminSpreadFeeE6_)    / spreadSumE6;
spreadFee0ToProtocolScaled = (surplus0Scaled * protocolSpreadFeeE6_) / spreadSumE6;
``` [1](#0-0) 

Because `adminSpreadFeeE6_ + protocolSpreadFeeE6_ = spreadSumE6`, the two terms sum to `surplus0Scaled` (minus at most 1 unit of floor rounding). The function then **additionally** pays out the full notional accumulator:

```solidity
notionalFee0ToProtocolScaled = notionalFee0AmountScaled - notionalFee0ToAdminScaled;
``` [2](#0-1) 

Total scaled payout ≈ `surplus0Scaled + notionalFee0AmountScaled`.  
Available scaled balance = `surplus0Scaled`.  
**Over-allocation = `notionalFee0AmountScaled`.**

The codebase itself documents this in a test that explicitly asserts the over-allocation occurs:

```solidity
assertGt(total0Attempted, surplus0Scaled, "token0 attempted payout exceeds computed surplus");
assertGt(total1Attempted, surplus1Scaled, "token1 attempted payout exceeds computed surplus");
``` [3](#0-2) 

Because the pool's ERC-20 balance also contains LP tokens (tracked in `binTotals`), the `safeTransfer` calls succeed as long as `notionalFee0AmountScaled ≤ binTotals.scaledToken0` (almost always true). The extra tokens are silently taken from LP bin balances, reducing the amount LPs can withdraw.

The fee collection is permissionless — anyone can call `collectPoolFees` on the factory:

```solidity
function collectPoolFees(address pool) external override nonReentrant {
``` [4](#0-3) 

---

### Impact Explanation

Every `collectPoolFees` call when both `spreadFeeE6 > 0` and `notionalFeeE8 > 0` drains `notionalFee0AmountScaled / TOKEN_0_SCALE_MULTIPLIER` tokens from LP bin balances. For 18-decimal tokens (`TOKEN_0_SCALE_MULTIPLIER = 1`), the loss equals the full notional accumulator in token units. The loss compounds with swap volume: more swaps → larger notional accumulator → larger LP drain per collection call. LPs cannot recover these tokens via `removeLiquidity` because `binTotals` is decremented by the over-transfer. [5](#0-4) 

---

### Likelihood Explanation

The production fee model is designed to use both spread fees and notional fees simultaneously (the factory exposes `setPoolFees` combining both). Any pool with both fee types active and non-zero accumulated notional fees is vulnerable. `collectPoolFees` is permissionless, so any external actor can trigger the drain repeatedly. [6](#0-5) 

---

### Recommendation

Before computing the spread-fee base, subtract the notional accumulator from the surplus so the two fee pools are disjoint:

```solidity
uint256 spreadSurplus0Scaled = surplus0Scaled > notionalFee0AmountScaled
    ? surplus0Scaled - notionalFee0AmountScaled : 0;
uint256 spreadSurplus1Scaled = surplus1Scaled > notionalFee1AmountScaled
    ? surplus1Scaled - notionalFee1AmountScaled : 0;

uint256 spreadFee0ToAdminScaled = spreadSumE6 == 0 ? 0
    : (spreadSurplus0Scaled * adminSpreadFeeE6_) / spreadSumE6;
// ... use spreadSurplus* throughout
```

This ensures the spread-fee payout is bounded by the LP-fee surplus and the notional-fee payout is bounded by the notional accumulator, with no overlap.

---

### Proof of Concept

1. Deploy a pool with `protocolSpreadFeeE6 = 500_000` (50%) and `protocolNotionalFeeE8 = 1_000_000` (1%).
2. Add liquidity and execute several swaps to accumulate both spread fees and notional fees.
3. Read `notionalFeeToken0Scaled` (call it `N`) and compute `surplus0Scaled` (call it `S`).
4. Call `factory.collectPoolFees(pool)`.
5. Observe that the pool transferred `S + N` scaled units worth of token0 in total (spread payout ≈ `S`, notional payout = `N`), but only `S` was available as surplus.
6. Read `binTotals.scaledToken0` before and after — it decreases by `N` scaled units, confirming LP principal was consumed.

The existing test `test_collectProtocolFees_math_overallocates_whenSpreadAndNotionalBothActive` already proves step 5 mathematically without executing the transfer: [7](#0-6)

### Citations

**File:** metric-core/contracts/MetricOmmPool.sol (L391-395)
```text
      uint256 spreadFee0ToAdminScaled = spreadSumE6 == 0 ? 0 : (surplus0Scaled * adminSpreadFeeE6_) / spreadSumE6;
      uint256 spreadFee1ToAdminScaled = spreadSumE6 == 0 ? 0 : (surplus1Scaled * adminSpreadFeeE6_) / spreadSumE6;

      uint256 spreadFee0ToProtocolScaled = spreadSumE6 == 0 ? 0 : (surplus0Scaled * protocolSpreadFeeE6_) / spreadSumE6;
      uint256 spreadFee1ToProtocolScaled = spreadSumE6 == 0 ? 0 : (surplus1Scaled * protocolSpreadFeeE6_) / spreadSumE6;
```

**File:** metric-core/contracts/MetricOmmPool.sol (L402-403)
```text
      uint256 notionalFee0ToProtocolScaled = notionalFee0AmountScaled - notionalFee0ToAdminScaled;
      uint256 notionalFee1ToProtocolScaled = notionalFee1AmountScaled - notionalFee1ToAdminScaled;
```

**File:** metric-core/contracts/MetricOmmPool.sol (L411-414)
```text
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

**File:** metric-core/contracts/MetricOmmPoolFactory.sol (L379-389)
```text
  function collectPoolFees(address pool) external override nonReentrant {
    PoolFeeConfig memory c = poolFeeConfig[pool];
    IMetricOmmPoolCollectFees(pool)
      .collectFees(
        c.protocolSpreadFeeE6,
        c.adminSpreadFeeE6,
        c.protocolNotionalFeeE8,
        c.adminNotionalFeeE8,
        poolAdminFeeDestination[pool]
      );
  }
```
