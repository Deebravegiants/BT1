### Title
`notionalFeeToken0Scaled`/`notionalFeeToken1Scaled` Cleared to Zero Even When No Tokens Are Transferred, Permanently Losing Accumulated Notional Fees - (File: `metric-core/contracts/MetricOmmPool.sol`)

### Summary

In `MetricOmmPool.collectFees`, the notional fee accumulators `notionalFeeToken0Scaled` and `notionalFeeToken1Scaled` are unconditionally reset to zero even when the scaled fee amounts round down to zero external token units. This permanently destroys accumulated protocol/admin fee revenue without any corresponding token transfer.

### Finding Description

`collectFees` computes the total scaled fee amounts, converts them to external token units using `Math.Rounding.Floor`, conditionally transfers only if the external amount is `> 0`, and then **unconditionally** clears both notional accumulators:

```solidity
// metric-core/contracts/MetricOmmPool.sol lines 411-430
(uint256 totalFee0ToAdmin, uint256 totalFee1ToAdmin) =
    deltasScaledToExternal(totalFee0ToAdminScaled, totalFee1ToAdminScaled, Math.Rounding.Floor);
(uint256 totalFee0ToProtocol, uint256 totalFee1ToProtocol) =
    deltasScaledToExternal(totalFee0ToProtocolScaled, totalFee1ToProtocolScaled, Math.Rounding.Floor);

if (totalFee0ToAdmin > 0) { transferToken0(adminFeeDestination_, totalFee0ToAdmin); }
if (totalFee1ToAdmin > 0) { transferToken1(adminFeeDestination_, totalFee1ToAdmin); }
if (totalFee0ToProtocol > 0) { transferToken0(FACTORY, totalFee0ToProtocol); }
if (totalFee1ToProtocol > 0) { transferToken1(FACTORY, totalFee1ToProtocol); }

notionalFeeToken0Scaled = 0;   // ← always cleared
notionalFeeToken1Scaled = 0;   // ← always cleared
``` [1](#0-0) 

The floor-division conversion is:

```solidity
deltaAmount0 = scaledDeltaAmount0 / TOKEN_0_SCALE_MULTIPLIER;
``` [2](#0-1) 

For tokens with fewer than 18 decimals (e.g. USDC, 6 decimals), `TOKEN_0_SCALE_MULTIPLIER = 10^12`. Any accumulated `notionalFeeToken0Scaled < 10^12` rounds to 0 external USDC. The accumulator is still zeroed, and those scaled units are orphaned inside the pool.

After the reset, the orphaned tokens remain in the pool's ERC-20 balance but are no longer tracked by `binTotals.scaledToken0` or `notionalFeeToken0Scaled`. On the next `collectFees` call the surplus formula is:

```solidity
surplus0Scaled = balance0() * TOKEN_0_SCALE_MULTIPLIER
               - uint256(binTotals.scaledToken0)
               - notionalFee0AmountScaled;   // now 0
``` [3](#0-2) 

The orphaned tokens now appear as spread-fee surplus. In pools configured with **only notional fees and zero spread fees** (a valid and tested configuration — `protocolSpreadFeeE6 = 0, adminSpreadFeeE6 = 0`), `spreadFee0ToAdminScaled` and `spreadFee0ToProtocolScaled` are both 0, so the orphaned tokens are **never distributed** and remain permanently stuck in the pool.

The trigger is fully unprivileged: `MetricOmmPoolFactory.collectPoolFees(pool)` is callable by anyone with no access control:

```solidity
function collectPoolFees(address pool) external override nonReentrant {
``` [4](#0-3) 

### Impact Explanation

**Direct loss of protocol and admin fee revenue.** Accumulated notional fees paid by traders (who already paid the higher swap cost) are permanently destroyed — neither the protocol nor the admin ever receives them. In a notional-only fee pool (spread fees = 0), the orphaned tokens can never be recovered. The maximum loss per `collectFees` invocation is `TOKEN_0_SCALE_MULTIPLIER − 1` scaled units per token per recipient leg (up to ~2 USDC per call for a USDC/X pool). An adversary can call `collectPoolFees` repeatedly after each small swap to drain the notional fee accumulator in dust increments, causing unbounded cumulative loss.

### Likelihood Explanation

- `collectPoolFees` is callable by any address with no restriction.
- Pools pairing 18-decimal tokens with low-decimal tokens (USDC, USDT) are the primary deployment target.
- Small swaps generating sub-unit notional fees are routine in any active pool.
- No special setup or privileged access is required.

### Recommendation

Only clear `notionalFeeToken0Scaled` / `notionalFeeToken1Scaled` by the amount actually transferred (in scaled units), not unconditionally to zero. Compute the scaled equivalent of the external amount transferred and subtract only that:

```diff
-     notionalFeeToken0Scaled = 0;
-     notionalFeeToken1Scaled = 0;
+     // Subtract only the scaled amount that was actually paid out
+     uint256 paid0Scaled = totalFee0ToAdmin * TOKEN_0_SCALE_MULTIPLIER
+                         + totalFee0ToProtocol * TOKEN_0_SCALE_MULTIPLIER;
+     uint256 paid1Scaled = totalFee1ToAdmin * TOKEN_1_SCALE_MULTIPLIER
+                         + totalFee1ToProtocol * TOKEN_1_SCALE_MULTIPLIER;
+     notionalFeeToken0Scaled = uint128(notionalFee0AmountScaled > paid0Scaled
+         ? notionalFee0AmountScaled - paid0Scaled : 0);
+     notionalFeeToken1Scaled = uint128(notionalFee1AmountScaled > paid1Scaled
+         ? notionalFee1AmountScaled - paid1Scaled : 0);
```

Alternatively, only call `collectFees` when the accumulated scaled amount is large enough to produce at least 1 external unit, or enforce a minimum accumulation threshold before clearing.

### Proof of Concept

1. Deploy a pool with USDC (6 decimals) as token0 and an 18-decimal token as token1. Set `protocolNotionalFeeE8 = 1_000_000` (1%), `protocolSpreadFeeE6 = 0`, `adminSpreadFeeE6 = 0`.
2. `TOKEN_0_SCALE_MULTIPLIER = 10^12`.
3. Execute a swap that produces `notionalFeeToken0Scaled = 5 * 10^11` (< `10^12`). This requires a token0 output of ~0.5 USDC, a realistic small swap.
4. Any address calls `factory.collectPoolFees(pool)`.
5. Inside `collectFees`: `totalFee0ToProtocol = (5 * 10^11) / 10^12 = 0` (floor division). No transfer occurs.
6. `notionalFeeToken0Scaled` is set to 0.
7. The 5 * 10^11 scaled units (~0.5 USDC worth) remain in the pool's ERC-20 balance but are now untracked.
8. On the next `collectFees` call, `surplus0Scaled` includes these orphaned units, but since `spreadSumE6 = 0`, `spreadFee0ToProtocolScaled = 0` and `spreadFee0ToAdminScaled = 0`. The tokens are never distributed.
9. Repeat steps 3–8 to accumulate unbounded losses.

### Citations

**File:** metric-core/contracts/MetricOmmPool.sol (L385-388)
```text
    uint256 surplus0Scaled =
      balance0() * TOKEN_0_SCALE_MULTIPLIER - uint256(binTotals.scaledToken0) - notionalFee0AmountScaled;
    uint256 surplus1Scaled =
      balance1() * TOKEN_1_SCALE_MULTIPLIER - uint256(binTotals.scaledToken1) - notionalFee1AmountScaled;
```

**File:** metric-core/contracts/MetricOmmPool.sol (L411-430)
```text
      (uint256 totalFee0ToAdmin, uint256 totalFee1ToAdmin) =
        deltasScaledToExternal(totalFee0ToAdminScaled, totalFee1ToAdminScaled, Math.Rounding.Floor);
      (uint256 totalFee0ToProtocol, uint256 totalFee1ToProtocol) =
        deltasScaledToExternal(totalFee0ToProtocolScaled, totalFee1ToProtocolScaled, Math.Rounding.Floor);

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

      notionalFeeToken0Scaled = 0;
      notionalFeeToken1Scaled = 0;
```

**File:** metric-core/contracts/MetricOmmPool.sol (L617-628)
```text
  function deltasScaledToExternal(uint256 scaledDeltaAmount0, uint256 scaledDeltaAmount1, Math.Rounding rounding)
    internal
    view
    returns (uint256 deltaAmount0, uint256 deltaAmount1)
  {
    if (rounding == Math.Rounding.Ceil) {
      deltaAmount0 = Math.ceilDiv(scaledDeltaAmount0, TOKEN_0_SCALE_MULTIPLIER);
      deltaAmount1 = Math.ceilDiv(scaledDeltaAmount1, TOKEN_1_SCALE_MULTIPLIER);
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
