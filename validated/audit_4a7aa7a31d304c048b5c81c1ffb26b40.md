### Title
`setPoolAdminFeeDestination` Redirects Accumulated Admin Spread Fees to New Destination Without Prior Settlement — (`metric-core/contracts/MetricOmmPoolFactory.sol`)

### Summary

`setPoolAdminFeeDestination` updates `poolAdminFeeDestination[pool]` without first calling `collectFees`. All spread-fee surplus that accrued under the old destination is silently redirected to the new destination on the next `collectPoolFees` call, causing a direct loss of owed admin fees for the previous recipient.

### Finding Description

The factory exposes three fee-parameter mutators for the pool admin. Two of them — `setPoolAdminFees` and `setPoolProtocolFee` — explicitly call `collectFees` with the current rates and current destination **before** updating any state, ensuring that accumulated fees are settled to the correct recipient first. [1](#0-0) 

`setPoolAdminFeeDestination`, however, skips this settlement step entirely: [2](#0-1) 

The pool's `collectFees` function computes the admin share of the spread surplus as:

```
surplus0Scaled = balance0() * TOKEN_0_SCALE_MULTIPLIER
               - binTotals.scaledToken0
               - notionalFeeToken0Scaled
```

and routes the admin portion to whatever address is stored in `poolAdminFeeDestination[pool]` **at collection time**: [3](#0-2) 

Because the surplus is a running balance (not per-epoch snapshots), every unit of spread fee that accumulated while the old destination was set is included in the next collection call — and that collection now uses the new destination.

### Impact Explanation

The pool admin can atomically:
1. Call `setPoolAdminFeeDestination(pool, attackerAddress)` — no settlement occurs; all prior surplus remains on the pool.
2. Call `collectPoolFees(pool)` (permissionless) — the entire accumulated admin spread surplus, including fees earned under the old destination, is transferred to `attackerAddress`.

The old admin fee destination (which may be a separate DAO treasury, multisig, or LP-revenue recipient) receives nothing for the period it was the designated recipient. The loss is bounded by the total admin spread surplus at the time of the destination change, which grows with swap volume and time since the last collection.

The notional fee accumulators (`notionalFeeToken0Scaled` / `notionalFeeToken1Scaled`) are also split using the destination passed at collection time, so those are equally affected. [4](#0-3) 

### Likelihood Explanation

The pool admin is a per-pool privileged role, not the factory owner. The admin fee destination is frequently a separate entity (e.g., a DAO treasury or a revenue-sharing contract distinct from the admin key). Any pool admin who controls both the admin key and a new destination address can execute this in a single block. `collectPoolFees` is permissionless, so the admin does not even need a second transaction — they can bundle both calls. No timelock or cap check guards `setPoolAdminFeeDestination`. [5](#0-4) 

### Recommendation

Mirror the pattern used by `setPoolAdminFees` and `setPoolProtocolFee`: call `collectFees` with the **current** rates and the **current** destination before overwriting `poolAdminFeeDestination[pool]`.

```solidity
function setPoolAdminFeeDestination(address pool, address newAdminFeeDestination)
    external override nonReentrant onlyPoolAdmin(pool)
{
    if (newAdminFeeDestination == address(0)) revert InvalidAdminFeeDestination();

    // Settle accumulated fees to the OLD destination before switching.
    PoolFeeConfig memory c = poolFeeConfig[pool];
    IMetricOmmPoolCollectFees(pool).collectFees(
        c.protocolSpreadFeeE6,
        c.adminSpreadFeeE6,
        c.protocolNotionalFeeE8,
        c.adminNotionalFeeE8,
        poolAdminFeeDestination[pool]   // old destination
    );

    poolAdminFeeDestination[pool] = newAdminFeeDestination;
    emit PoolAdminFeeDestinationUpdated(pool, newAdminFeeDestination);
}
```

### Proof of Concept

```
Setup:
  - Pool deployed with adminFeeDestination = treasury (separate multisig)
  - Pool accumulates 1 000 000 units of spread surplus over N swaps
  - adminSpreadFeeE6 = 50 000 (5%), protocolSpreadFeeE6 = 10 000 (1%)
  - Admin share of surplus ≈ 833 333 units (5/6 of total fee share)

Attack:
  1. pool_admin calls setPoolAdminFeeDestination(pool, attacker_wallet)
     → poolAdminFeeDestination[pool] = attacker_wallet
     → NO collectFees called; surplus stays on pool

  2. Anyone calls collectPoolFees(pool)
     → surplus0Scaled = 1 000 000
     → spreadFee0ToAdmin = 1 000 000 * 50 000 / 60 000 ≈ 833 333 → sent to attacker_wallet
     → spreadFee0ToProtocol ≈ 166 667 → sent to FACTORY

Result:
  treasury receives 0 (should have received ≈ 833 333)
  attacker_wallet receives ≈ 833 333 (earned under treasury's tenure)
``` [2](#0-1) [6](#0-5)

### Citations

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

**File:** metric-core/contracts/MetricOmmPoolFactory.sol (L408-435)
```text
  function setPoolAdminFees(address pool, uint24 newAdminSpreadFeeE6, uint24 newAdminNotionalFeeE8)
    external
    override
    nonReentrant
    onlyPoolAdmin(pool)
  {
    if (newAdminSpreadFeeE6 > maxAdminSpreadFeeE6) revert AdminFeeTooHigh();
    if (newAdminNotionalFeeE8 > maxAdminNotionalFeeE8) revert AdminFeeTooHigh();

    PoolFeeConfig memory c = poolFeeConfig[pool];
    IMetricOmmPoolCollectFees(pool)
      .collectFees(
        c.protocolSpreadFeeE6,
        c.adminSpreadFeeE6,
        c.protocolNotionalFeeE8,
        c.adminNotionalFeeE8,
        poolAdminFeeDestination[pool]
      );

    c.adminSpreadFeeE6 = newAdminSpreadFeeE6;
    c.adminNotionalFeeE8 = newAdminNotionalFeeE8;
    poolFeeConfig[pool] = c;

    IMetricOmmPoolFactoryActions(pool)
      .setPoolFees(c.protocolSpreadFeeE6 + c.adminSpreadFeeE6, c.protocolNotionalFeeE8 + c.adminNotionalFeeE8);
    emit PoolAdminSpreadFeeUpdated(pool, newAdminSpreadFeeE6);
    emit PoolAdminNotionalFeeUpdated(pool, newAdminNotionalFeeE8);
  }
```

**File:** metric-core/contracts/MetricOmmPoolFactory.sol (L438-447)
```text
  function setPoolAdminFeeDestination(address pool, address newAdminFeeDestination)
    external
    override
    nonReentrant
    onlyPoolAdmin(pool)
  {
    if (newAdminFeeDestination == address(0)) revert InvalidAdminFeeDestination();
    poolAdminFeeDestination[pool] = newAdminFeeDestination;
    emit PoolAdminFeeDestinationUpdated(pool, newAdminFeeDestination);
  }
```

**File:** metric-core/contracts/MetricOmmPool.sol (L385-421)
```text
    uint256 surplus0Scaled =
      balance0() * TOKEN_0_SCALE_MULTIPLIER - uint256(binTotals.scaledToken0) - notionalFee0AmountScaled;
    uint256 surplus1Scaled =
      balance1() * TOKEN_1_SCALE_MULTIPLIER - uint256(binTotals.scaledToken1) - notionalFee1AmountScaled;

    unchecked {
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

      if (totalFee0ToAdmin > 0) {
        transferToken0(adminFeeDestination_, totalFee0ToAdmin);
      }
      if (totalFee1ToAdmin > 0) {
        transferToken1(adminFeeDestination_, totalFee1ToAdmin);
      }
```
