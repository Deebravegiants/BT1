### Title
Missing `collectFees` Before `setPoolAdminFeeDestination` Redirects Accrued Admin Fees to New Destination — (`metric-core/contracts/MetricOmmPoolFactory.sol`)

### Summary

`MetricOmmPoolFactory.setPoolAdminFeeDestination` changes the admin fee sweep address without first flushing accrued spread-fee surplus and notional fees to the old destination. Every other fee-config mutator (`setPoolAdminFees`, `setPoolProtocolFee`) calls `collectFees` with the old config before writing new state. `setPoolAdminFeeDestination` omits this step, so all fees that accrued under the old destination are silently redirected to the new one on the next collection.

---

### Finding Description

The pool maintains two fee pools:

1. **Spread-fee surplus** — the implicit balance `balance(token) × scale − binTotals.scaledToken − notionalFeeTokenScaled`. This grows with every swap as the spread margin stays in the pool rather than entering bins.
2. **Notional fees** — explicitly tracked in `notionalFeeToken0Scaled` / `notionalFeeToken1Scaled`.

Both are distributed to `adminFeeDestination_` (the address passed into `collectFees`) when collection occurs.

`setPoolAdminFees` and `setPoolProtocolFee` both flush accrued fees to the **current** destination before updating state: [1](#0-0) [2](#0-1) 

`setPoolAdminFeeDestination` does **not**: [3](#0-2) 

After the destination is overwritten, every subsequent `collectFees` call — whether triggered by `collectPoolFees`, `setPoolAdminFees`, or `setPoolProtocolFee` — reads the **new** `poolAdminFeeDestination[pool]` and sends all accumulated fees there: [4](#0-3) 

The `collectFees` implementation on the pool transfers the admin share to whatever `adminFeeDestination_` it receives: [5](#0-4) 

---

### Impact Explanation

The old admin fee destination loses all spread-fee surplus and notional fees that accrued before the destination change. These are real ERC-20 token balances already held by the pool and owed to the old destination. The new destination receives tokens it was never entitled to. The magnitude scales with trading volume and time elapsed since the last collection.

---

### Likelihood Explanation

The pool admin is a semi-trusted, unprivileged-relative-to-factory role that can call `setPoolAdminFeeDestination` at any time without restriction beyond the `onlyPoolAdmin` check. The old and new fee destinations are independent addresses (e.g., a DAO treasury vs. a new multisig). Any routine destination rotation — a common operational action — silently triggers the loss. No attacker cooperation is required; the pool admin's own normal workflow is sufficient.

---

### Recommendation

Call `collectFees` with the current config and current destination before overwriting `poolAdminFeeDestination[pool]`, mirroring the pattern in `setPoolAdminFees`:

```solidity
function setPoolAdminFeeDestination(address pool, address newAdminFeeDestination)
    external
    override
    nonReentrant
    onlyPoolAdmin(pool)
{
    if (newAdminFeeDestination == address(0)) revert InvalidAdminFeeDestination();
    // Flush accrued fees to the OLD destination before rotating.
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

---

### Proof of Concept

1. Pool accumulates 1 000 token0 of spread-fee surplus and 500 token0 of notional fees over N swaps. Admin fee destination is `oldDest`.
2. Pool admin calls `setPoolAdminFeeDestination(pool, newDest)`. No `collectFees` is triggered; `poolAdminFeeDestination[pool]` is now `newDest`.
3. Anyone calls `collectPoolFees(pool)`. Inside, `collectFees` is invoked with `adminFeeDestination_ = newDest`.
4. `oldDest` receives 0 tokens. `newDest` receives the full admin share of 1 500 token0 worth of fees that accrued before the destination change. [6](#0-5) [7](#0-6)

### Citations

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

**File:** metric-core/contracts/MetricOmmPoolFactory.sol (L417-425)
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

**File:** metric-core/contracts/MetricOmmPool.sol (L382-388)
```text
    uint256 notionalFee0AmountScaled = notionalFeeToken0Scaled;
    uint256 notionalFee1AmountScaled = notionalFeeToken1Scaled;

    uint256 surplus0Scaled =
      balance0() * TOKEN_0_SCALE_MULTIPLIER - uint256(binTotals.scaledToken0) - notionalFee0AmountScaled;
    uint256 surplus1Scaled =
      balance1() * TOKEN_1_SCALE_MULTIPLIER - uint256(binTotals.scaledToken1) - notionalFee1AmountScaled;
```

**File:** metric-core/contracts/MetricOmmPool.sol (L416-421)
```text
      if (totalFee0ToAdmin > 0) {
        transferToken0(adminFeeDestination_, totalFee0ToAdmin);
      }
      if (totalFee1ToAdmin > 0) {
        transferToken1(adminFeeDestination_, totalFee1ToAdmin);
      }
```

**File:** metric-core/contracts/MetricOmmPool.sol (L429-430)
```text
      notionalFeeToken0Scaled = 0;
      notionalFeeToken1Scaled = 0;
```
