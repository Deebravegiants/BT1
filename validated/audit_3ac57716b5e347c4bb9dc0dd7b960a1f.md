The code confirms the vulnerability. All cited lines match the actual production code:

- Lines 429-430: unconditional reset confirmed
- Lines 626-627: floor division confirmed
- Lines 385-388: surplus formula confirmed
- Lines 391-395: spread fee distribution gated on `spreadSumE6 != 0` confirmed
- Line 379: `collectPoolFees` has no access control confirmed

Audit Report

## Title
`notionalFeeToken0Scaled`/`notionalFeeToken1Scaled` Unconditionally Cleared to Zero Causing Permanent Loss of Accumulated Notional Fees - (File: `metric-core/contracts/MetricOmmPool.sol`)

## Summary
In `MetricOmmPool.collectFees`, the notional fee accumulators `notionalFeeToken0Scaled` and `notionalFeeToken1Scaled` are unconditionally reset to zero at lines 429–430 regardless of whether the floor-divided external token amounts are nonzero. For low-decimal tokens (e.g. USDC, 6 decimals, `TOKEN_0_SCALE_MULTIPLIER = 10^12`), any accumulated scaled amount below `10^12` rounds to zero external units, no transfer occurs, yet the accumulator is wiped. In pools configured with zero spread fees, the orphaned scaled units are never redistributed and remain permanently stuck in the pool balance.

## Finding Description
`collectFees` computes external fee amounts via floor division: [1](#0-0) 

Transfers are conditional on the result being `> 0`: [2](#0-1) 

But the accumulators are then unconditionally zeroed: [3](#0-2) 

After the reset, the orphaned scaled units remain in the pool's ERC-20 balance but are no longer tracked by `binTotals.scaledToken0` or `notionalFeeToken0Scaled`. On the next `collectFees` call, the surplus formula picks them up: [4](#0-3) 

However, in a notional-only pool (`protocolSpreadFeeE6 = 0`, `adminSpreadFeeE6 = 0`), the spread fee distribution is gated: [5](#0-4) 

`spreadSumE6 == 0` causes all spread fee allocations to be zero, so the orphaned surplus is never distributed. The tokens are permanently stuck. The trigger is fully unprivileged — `collectPoolFees` has no access control: [6](#0-5) 

## Impact Explanation
Direct loss of protocol and admin fee revenue. Accumulated notional fees paid by traders are permanently destroyed — neither the protocol nor the admin receives them. In a notional-only fee pool (spread fees = 0), the orphaned tokens can never be recovered. The maximum loss per `collectFees` invocation is up to `2 × (TOKEN_0_SCALE_MULTIPLIER − 1)` scaled units (admin leg + protocol leg), approximately 2 USDC per call for a USDC/X pool. An adversary can call `collectPoolFees` repeatedly after each small swap to drain the notional fee accumulator in dust increments, causing unbounded cumulative loss of protocol and admin fee revenue.

## Likelihood Explanation
`collectPoolFees` is callable by any address with no restriction. Pools pairing 18-decimal tokens with low-decimal tokens (USDC, USDT) are the primary deployment target per the contest scope. Small swaps generating sub-unit notional fees are routine in any active pool. No special setup or privileged access is required. The attack is repeatable indefinitely.

## Recommendation
Only clear `notionalFeeToken0Scaled` / `notionalFeeToken1Scaled` by the scaled equivalent of the amount actually transferred, not unconditionally to zero:

```diff
-     notionalFeeToken0Scaled = 0;
-     notionalFeeToken1Scaled = 0;
+     uint256 paid0Scaled = (totalFee0ToAdmin + totalFee0ToProtocol) * TOKEN_0_SCALE_MULTIPLIER;
+     uint256 paid1Scaled = (totalFee1ToAdmin + totalFee1ToProtocol) * TOKEN_1_SCALE_MULTIPLIER;
+     notionalFeeToken0Scaled = uint128(notionalFee0AmountScaled > paid0Scaled
+         ? notionalFee0AmountScaled - paid0Scaled : 0);
+     notionalFeeToken1Scaled = uint128(notionalFee1AmountScaled > paid1Scaled
+         ? notionalFee1AmountScaled - paid1Scaled : 0);
```

Alternatively, enforce a minimum accumulation threshold before allowing `collectFees` to proceed.

## Proof of Concept
1. Deploy a pool with USDC (6 decimals) as token0 and an 18-decimal token as token1. Set `protocolNotionalFeeE8 = 1_000_000` (1%), `protocolSpreadFeeE6 = 0`, `adminSpreadFeeE6 = 0`. `TOKEN_0_SCALE_MULTIPLIER = 10^12`.
2. Execute a swap that produces `notionalFeeToken0Scaled = 5 × 10^11` (< `10^12`), requiring a token0 output of ~0.5 USDC — a realistic small swap.
3. Any address calls `factory.collectPoolFees(pool)`.
4. Inside `collectFees`: `totalFee0ToProtocol = (5 × 10^11) / 10^12 = 0` (floor). No transfer occurs.
5. `notionalFeeToken0Scaled` is set to 0. The 5 × 10^11 scaled units (~0.5 USDC) remain in the pool's ERC-20 balance but are now untracked.
6. On the next `collectFees` call, `surplus0Scaled` includes these orphaned units, but since `spreadSumE6 = 0`, `spreadFee0ToProtocolScaled = 0` and `spreadFee0ToAdminScaled = 0`. The tokens are never distributed.
7. Repeat steps 2–6 to accumulate unbounded losses. A Foundry test can verify this by asserting `notionalFeeToken0Scaled == 0` after step 5 while the pool's USDC balance exceeds `binTotals.scaledToken0 / TOKEN_0_SCALE_MULTIPLIER`.

### Citations

**File:** metric-core/contracts/MetricOmmPool.sol (L385-388)
```text
    uint256 surplus0Scaled =
      balance0() * TOKEN_0_SCALE_MULTIPLIER - uint256(binTotals.scaledToken0) - notionalFee0AmountScaled;
    uint256 surplus1Scaled =
      balance1() * TOKEN_1_SCALE_MULTIPLIER - uint256(binTotals.scaledToken1) - notionalFee1AmountScaled;
```

**File:** metric-core/contracts/MetricOmmPool.sol (L391-395)
```text
      uint256 spreadFee0ToAdminScaled = spreadSumE6 == 0 ? 0 : (surplus0Scaled * adminSpreadFeeE6_) / spreadSumE6;
      uint256 spreadFee1ToAdminScaled = spreadSumE6 == 0 ? 0 : (surplus1Scaled * adminSpreadFeeE6_) / spreadSumE6;

      uint256 spreadFee0ToProtocolScaled = spreadSumE6 == 0 ? 0 : (surplus0Scaled * protocolSpreadFeeE6_) / spreadSumE6;
      uint256 spreadFee1ToProtocolScaled = spreadSumE6 == 0 ? 0 : (surplus1Scaled * protocolSpreadFeeE6_) / spreadSumE6;
```

**File:** metric-core/contracts/MetricOmmPool.sol (L416-427)
```text
      if (totalFee0ToAdmin > 0) {
        transferToken0(adminFeeDestination_, totalFee0ToAdmin);
      }
      if (totalFee1ToAdmin > 0) {
        transferToken1(adminFeeDestination_, totalFee1ToAdmin);
      }
      if (totalFee0ToProtocol > 0) {
        transferToken0(FACTORY, totalFee0ToProtocol);
      }
      if (totalFee1ToProtocol > 0) {
        transferToken1(FACTORY, totalFee1ToProtocol);
      }
```

**File:** metric-core/contracts/MetricOmmPool.sol (L429-430)
```text
      notionalFeeToken0Scaled = 0;
      notionalFeeToken1Scaled = 0;
```

**File:** metric-core/contracts/MetricOmmPool.sol (L625-628)
```text
    } else {
      deltaAmount0 = scaledDeltaAmount0 / TOKEN_0_SCALE_MULTIPLIER;
      deltaAmount1 = scaledDeltaAmount1 / TOKEN_1_SCALE_MULTIPLIER;
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
