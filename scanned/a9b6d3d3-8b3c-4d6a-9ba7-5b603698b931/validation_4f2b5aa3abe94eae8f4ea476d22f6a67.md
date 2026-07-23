### Title
`setPoolAdminFeeDestination` Does Not Settle Pending Fees Before Changing the Admin Fee Destination — (File: metric-core/contracts/MetricOmmPoolFactory.sol)

### Summary

`MetricOmmPoolFactory.setPoolAdminFeeDestination` updates `poolAdminFeeDestination[pool]` without first calling `collectFees` to flush accrued admin fees to the old destination. Every other fee-parameter mutator (`setPoolAdminFees`, `setPoolProtocolFee`) explicitly collects first. The omission means all pending admin fees — both the spread surplus and the `notionalFeeToken0Scaled`/`notionalFeeToken1Scaled` accumulators — are silently redirected to the new destination when `collectPoolFees` is eventually called, causing a direct loss for the old fee destination.

### Finding Description

The pool has two pending admin fee pools at any point in time:

1. **Spread surplus** — `balance(token) × scaleMultiplier − binTotals.scaledToken − notionalFeeScaled`. This surplus is split between admin and protocol at collection time using the stored `adminSpreadFeeE6 / protocolSpreadFeeE6` ratio.
2. **Notional fee accumulators** — `notionalFeeToken0Scaled` and `notionalFeeToken1Scaled` (slot 2), incremented on every swap proportional to `notionalFeeE8`.

Both are flushed and sent to `adminFeeDestination_` only when `collectFees` is called.

`setPoolAdminFees` and `setPoolProtocolFee` both call `collectFees` before mutating any fee parameter:

```solidity
// setPoolAdminFees — collects first ✓
IMetricOmmPoolCollectFees(pool).collectFees(
    c.protocolSpreadFeeE6, c.adminSpreadFeeE6,
    c.protocolNotionalFeeE8, c.adminNotionalFeeE8,
    poolAdminFeeDestination[pool]   // old destination
);
c.adminSpreadFeeE6 = newAdminSpreadFeeE6;
...
```

`setPoolAdminFeeDestination` does not:

```solidity
// setPoolAdminFeeDestination — no collection ✗
function setPoolAdminFeeDestination(address pool, address newAdminFeeDestination)
    external override nonReentrant onlyPoolAdmin(pool)
{
    if (newAdminFeeDestination == address(0)) revert InvalidAdminFeeDestination();
    poolAdminFeeDestination[pool] = newAdminFeeDestination;   // overwrites without flush
    emit PoolAdminFeeDestinationUpdated(pool, newAdminFeeDestination);
}
```

After the overwrite, any subsequent call to `collectPoolFees` (which is permissionless) reads the new destination and sends all previously accrued admin fees there.

### Impact Explanation

All admin fees that accrued while the old destination was set are permanently redirected to the new destination. The old fee destination receives nothing for the period it was active. This is a direct, irreversible loss of real token balances (both token0 and token1) for the old admin fee destination. The magnitude equals the full admin share of all spread surplus and notional fee accumulators outstanding at the time of the destination change.

### Likelihood Explanation

The pool admin role is expected to change the fee destination during normal operations (treasury rotation, multisig migration, admin transfer handover). The two-step admin transfer (`proposePoolAdminTransfer` / `acceptPoolAdmin`) makes this especially likely: a new admin accepting the role can immediately call `setPoolAdminFeeDestination` to redirect all fees accumulated under the previous admin's tenure. `collectPoolFees` is permissionless, so any keeper or bot can trigger the misdirected payout at any time after the destination is changed.

### Recommendation

Add a `collectFees` call at the top of `setPoolAdminFeeDestination`, mirroring the pattern used in `setPoolAdminFees` and `setPoolProtocolFee`:

```solidity
function setPoolAdminFeeDestination(address pool, address newAdminFeeDestination)
    external override nonReentrant onlyPoolAdmin(pool)
{
    if (newAdminFeeDestination == address(0)) revert InvalidAdminFeeDestination();

    // Flush pending fees to the OLD destination before switching.
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

1. Pool is deployed with `adminFeeDestination = Alice`.
2. Multiple swaps occur; `notionalFeeToken0Scaled` and `notionalFeeToken1Scaled` accumulate, and spread surplus grows.
3. Pool admin calls `setPoolAdminFeeDestination(pool, Bob)`. No fees are collected; `poolAdminFeeDestination[pool]` is overwritten to `Bob`.
4. Anyone calls `collectPoolFees(pool)`. The factory reads `poolAdminFeeDestination[pool] == Bob` and passes it to `collectFees`.
5. Inside `collectFees`, all admin-share tokens (spread + notional) are transferred to `Bob`.
6. `Alice` receives zero tokens despite being the fee destination for the entire accrual period.

**Relevant code locations:**

`setPoolAdminFeeDestination` — no pre-collection: [1](#0-0) 

`setPoolAdminFees` — correct pattern with pre-collection: [2](#0-1) 

`setPoolProtocolFee` — correct pattern with pre-collection: [3](#0-2) 

`collectFees` — uses `adminFeeDestination_` parameter to route admin tokens: [4](#0-3) 

`collectPoolFees` — permissionless, reads current `poolAdminFeeDestination`: [5](#0-4) 

Notional fee accumulators in pool storage (slot 2): [6](#0-5)

### Citations

**File:** metric-core/contracts/MetricOmmPoolFactory.sol (L318-360)
```text
  function setPoolProtocolFee(address pool, uint24 newProtocolSpreadFeeE6, uint24 newProtocolNotionalFeeE8)
    external
    override
    onlyOwner
    nonReentrant
  {
    if (newProtocolSpreadFeeE6 > maxProtocolSpreadFeeE6) revert ProtocolFeeTooHigh();
    if (newProtocolNotionalFeeE8 > maxProtocolNotionalFeeE8) revert ProtocolFeeTooHigh();

    PoolFeeConfig memory c = poolFeeConfig[pool];
    IMetricOmmPoolCollectFees(pool)
      .collectFees(
        c.protocolSpreadFeeE6,
        c.adminSpreadFeeE6,
        c.protocolNotionalFeeE8,
        c.adminNotionalFeeE8,
        poolAdminFeeDestination[pool]
      );

    uint24 aSpread = c.adminSpreadFeeE6;
    uint24 aNotional = c.adminNotionalFeeE8;
    if (aSpread > maxAdminSpreadFeeE6) {
      aSpread = maxAdminSpreadFeeE6;
      emit PoolAdminSpreadFeeUpdated(pool, aSpread);
    }
    if (aNotional > maxAdminNotionalFeeE8) {
      aNotional = maxAdminNotionalFeeE8;
      emit PoolAdminNotionalFeeUpdated(pool, aNotional);
    }

    c = PoolFeeConfig({
      protocolSpreadFeeE6: newProtocolSpreadFeeE6,
      adminSpreadFeeE6: aSpread,
      protocolNotionalFeeE8: newProtocolNotionalFeeE8,
      adminNotionalFeeE8: aNotional
    });
    poolFeeConfig[pool] = c;

    IMetricOmmPoolFactoryActions(pool)
      .setPoolFees(c.protocolSpreadFeeE6 + c.adminSpreadFeeE6, c.protocolNotionalFeeE8 + c.adminNotionalFeeE8);
    emit PoolProtocolSpreadFeeUpdated(pool, newProtocolSpreadFeeE6);
    emit PoolProtocolNotionalFeeUpdated(pool, newProtocolNotionalFeeE8);
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

**File:** metric-core/contracts/MetricOmmPool.sol (L83-86)
```text
  // Slot 2 ordering (from left to right):
  //   [16bytes notionalFeeToken1Scaled] [16bytes notionalFeeToken0Scaled]
  uint128 internal notionalFeeToken0Scaled;
  uint128 internal notionalFeeToken1Scaled;
```

**File:** metric-core/contracts/MetricOmmPool.sol (L365-434)
```text
  function collectFees(
    uint256 protocolSpreadFeeE6_,
    uint256 adminSpreadFeeE6_,
    uint256 protocolNotionalFeeE8_,
    uint256 adminNotionalFeeE8_,
    address adminFeeDestination_
  ) external onlyFactory nonReentrant(PoolActions.COLLECT_FEES) {
    uint256 spreadSumE6;
    uint256 notionalSumE8;
    unchecked {
      spreadSumE6 = protocolSpreadFeeE6_ + adminSpreadFeeE6_;
      notionalSumE8 = protocolNotionalFeeE8_ + adminNotionalFeeE8_;
      if (spreadSumE6 == 0 && notionalSumE8 == 0) {
        return;
      }
    }

    uint256 notionalFee0AmountScaled = notionalFeeToken0Scaled;
    uint256 notionalFee1AmountScaled = notionalFeeToken1Scaled;

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
      if (totalFee0ToProtocol > 0) {
        transferToken0(FACTORY, totalFee0ToProtocol);
      }
      if (totalFee1ToProtocol > 0) {
        transferToken1(FACTORY, totalFee1ToProtocol);
      }

      notionalFeeToken0Scaled = 0;
      notionalFeeToken1Scaled = 0;

      emit ProtocolFeesCollected(totalFee0ToProtocol, totalFee1ToProtocol, totalFee0ToAdmin, totalFee1ToAdmin);
    }
  }
```
