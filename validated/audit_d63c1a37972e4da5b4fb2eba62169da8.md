The code confirms all claims. Key observations:

- Lines 429-430: `notionalFeeToken0Scaled` and `notionalFeeToken1Scaled` are unconditionally zeroed.
- Lines 626-627: Floor division means any accumulated scaled amount below `TOKEN_0_SCALE_MULTIPLIER` rounds to 0 external units — no transfer occurs.
- Lines 416-427: Transfers are conditional on `> 0`, so nothing is sent when rounding produces zero.
- Lines 391-395: When `spreadSumE6 == 0`, spread fee allocations are hardcoded to 0, so orphaned tokens in the surplus are never distributed.
- Line 379: `collectPoolFees` has no access control beyond `nonReentrant`. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

---

Audit Report

## Title
`notionalFeeToken0Scaled`/`notionalFeeToken1Scaled` Cleared to Zero Even When No Tokens Are Transferred, Permanently Losing Accumulated Notional Fees - (File: `metric-core/contracts/MetricOmmPool.sol`)

## Summary
In `MetricOmmPool.collectFees`, the notional fee accumulators `notionalFeeToken0Scaled` and `notionalFeeToken1Scaled` are unconditionally reset to zero at lines 429–430 regardless of whether any tokens were actually transferred. When the accumulated scaled amount is below `TOKEN_0_SCALE_MULTIPLIER` (e.g., `10^12` for USDC with 6 decimals), floor division produces zero external units, no transfer occurs, yet the accumulator is still wiped. In pools configured with zero spread fees, the orphaned scaled units can never be recovered, causing permanent loss of protocol and admin fee revenue.

## Finding Description
`collectFees` (lines 370–434) computes `totalFee0ToProtocol` and `totalFee0ToAdmin` via `deltasScaledToExternal` with `Math.Rounding.Floor` (lines 411–414). The floor division at line 626 (`scaledDeltaAmount0 / TOKEN_0_SCALE_MULTIPLIER`) returns 0 whenever the accumulated scaled amount is less than `TOKEN_0_SCALE_MULTIPLIER`. The conditional transfers at lines 416–427 correctly skip the transfer when the result is 0. However, lines 429–430 then unconditionally zero both accumulators regardless of whether any transfer occurred.

On the next `collectFees` call, the surplus formula at lines 385–388 computes:
```
surplus0Scaled = balance0() * TOKEN_0_SCALE_MULTIPLIER - binTotals.scaledToken0 - notionalFee0AmountScaled
```
With `notionalFeeToken0Scaled` now 0, the orphaned scaled units appear as surplus. But when `spreadSumE6 == 0` (lines 391–395 short-circuit all spread allocations to 0), the surplus is never distributed to any recipient. The tokens remain permanently locked in the pool's ERC-20 balance, untracked by either `binTotals.scaledToken0` or `notionalFeeToken0Scaled`. No existing guard prevents this: the only check at lines 377–379 exits early only when both `spreadSumE6 == 0` and `notionalSumE8 == 0` simultaneously, which is not the case in a notional-only fee pool.

## Impact Explanation
Direct, permanent loss of protocol and admin fee revenue. Accumulated notional fees paid by traders are destroyed without any corresponding transfer. In a notional-only fee pool (`protocolSpreadFeeE6 = 0`, `adminSpreadFeeE6 = 0`), the orphaned tokens can never be recovered by any on-chain path. The maximum loss per invocation is up to `TOKEN_0_SCALE_MULTIPLIER − 1` scaled units per token per recipient leg (approaching 1 full external unit, e.g., ~1 USDC per call). An adversary can repeat this after every small swap to cause unbounded cumulative loss of protocol/admin fees, satisfying the direct loss of protocol fees threshold.

## Likelihood Explanation
`collectPoolFees` at line 379 of `MetricOmmPoolFactory.sol` is callable by any address with no access control beyond `nonReentrant`. Pools pairing 18-decimal tokens with low-decimal tokens (USDC, USDT) are the primary deployment target, making `TOKEN_0_SCALE_MULTIPLIER = 10^12` the common case. Small swaps generating sub-unit notional fees are routine in any active pool. No privileged access, special setup, or unusual conditions are required. The attack is fully repeatable after each small swap.

## Recommendation
Only subtract from `notionalFeeToken0Scaled`/`notionalFeeToken1Scaled` the scaled equivalent of what was actually paid out, rather than unconditionally zeroing:

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

Alternatively, enforce a minimum accumulation threshold before allowing `collectFees` to proceed, ensuring at least 1 external unit is transferable before clearing the accumulator.

## Proof of Concept
1. Deploy a pool with USDC (6 decimals) as token0 and an 18-decimal token as token1. Set `protocolNotionalFeeE8 = 1_000_000` (1%), `protocolSpreadFeeE6 = 0`, `adminSpreadFeeE6 = 0`. `TOKEN_0_SCALE_MULTIPLIER = 10^12`.
2. Execute a swap that produces `notionalFeeToken0Scaled = 5 * 10^11` (< `10^12`), requiring a token0 output of ~0.5 USDC — a realistic small swap.
3. Any address calls `factory.collectPoolFees(pool)`.
4. Inside `collectFees`: `totalFee0ToProtocol = (5 * 10^11) / 10^12 = 0` (floor). No transfer occurs.
5. `notionalFeeToken0Scaled` is set to 0. The 5 * 10^11 scaled units remain in the pool's ERC-20 balance but are now untracked.
6. On the next `collectFees` call, `surplus0Scaled` includes the orphaned units, but since `spreadSumE6 = 0`, `spreadFee0ToProtocolScaled = 0` and `spreadFee0ToAdminScaled = 0`. Tokens are never distributed.
7. Repeat steps 2–6 to accumulate unbounded losses of protocol fee revenue.

### Citations

**File:** metric-core/contracts/MetricOmmPool.sol (L391-395)
```text
      uint256 spreadFee0ToAdminScaled = spreadSumE6 == 0 ? 0 : (surplus0Scaled * adminSpreadFeeE6_) / spreadSumE6;
      uint256 spreadFee1ToAdminScaled = spreadSumE6 == 0 ? 0 : (surplus1Scaled * adminSpreadFeeE6_) / spreadSumE6;

      uint256 spreadFee0ToProtocolScaled = spreadSumE6 == 0 ? 0 : (surplus0Scaled * protocolSpreadFeeE6_) / spreadSumE6;
      uint256 spreadFee1ToProtocolScaled = spreadSumE6 == 0 ? 0 : (surplus1Scaled * protocolSpreadFeeE6_) / spreadSumE6;
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
