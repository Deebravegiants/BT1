### Title
Stale `poolAdminFeeDestination` After Admin Transfer Misdirects Accrued Admin Fees — (`metric-core/contracts/MetricOmmPoolFactory.sol`)

---

### Summary

`acceptPoolAdmin` updates `poolAdmin[pool]` but never touches `poolAdminFeeDestination[pool]`. Because `collectPoolFees` is permissionless, any caller can trigger fee collection immediately after the handover and send the entire admin share to the previous admin's fee destination. The new admin's own first call to `setPoolAdminFees` also internally collects fees to the stale address before the new admin has had a chance to update it.

---

### Finding Description

The two-step admin transfer in `MetricOmmPoolFactory` is:

1. Current admin calls `proposePoolAdminTransfer(pool, newAdmin)` — sets `pendingPoolAdmin[pool]`.
2. New admin calls `acceptPoolAdmin(pool)` — sets `poolAdmin[pool] = pending` and clears the pending slot.

`acceptPoolAdmin` only writes to `poolAdmin`:

```solidity
// MetricOmmPoolFactory.sol L518-526
function acceptPoolAdmin(address pool) external override nonReentrant {
    address pending = pendingPoolAdmin[pool];
    ...
    poolAdmin[pool] = pending;          // ← only this mapping is updated
    delete pendingPoolAdmin[pool];
    emit PoolAdminTransferred(pool, previousAdmin, pending);
}
```

`poolAdminFeeDestination[pool]` is a completely separate mapping that is **not touched**. It retains whatever address the previous admin last set.

`collectPoolFees` is **permissionless** — no `onlyPoolAdmin` guard:

```solidity
// MetricOmmPoolFactory.sol L379-389
function collectPoolFees(address pool) external override nonReentrant {
    PoolFeeConfig memory c = poolFeeConfig[pool];
    IMetricOmmPoolCollectFees(pool).collectFees(
        c.protocolSpreadFeeE6,
        c.adminSpreadFeeE6,
        c.protocolNotionalFeeE8,
        c.adminNotionalFeeE8,
        poolAdminFeeDestination[pool]   // ← stale old-admin address
    );
}
```

`setPoolAdminFees` (callable only by the new admin) also internally collects fees before updating rates, using the same stale destination:

```solidity
// MetricOmmPoolFactory.sol L418-425
IMetricOmmPoolCollectFees(pool).collectFees(
    c.protocolSpreadFeeE6,
    c.adminSpreadFeeE6,
    c.protocolNotionalFeeE8,
    c.adminNotionalFeeE8,
    poolAdminFeeDestination[pool]   // ← still stale at this point
);
```

Inside `MetricOmmPool.collectFees`, the admin share is transferred directly to whatever address is passed:

```solidity
// MetricOmmPool.sol L416-421
if (totalFee0ToAdmin > 0) {
    transferToken0(adminFeeDestination_, totalFee0ToAdmin);
}
if (totalFee1ToAdmin > 0) {
    transferToken1(adminFeeDestination_, totalFee1ToAdmin);
}
```

---

### Impact Explanation

All admin-share fees (both spread surplus and notional accumulator) that have accrued up to the moment of collection are transferred to the old admin's fee destination rather than the new admin's. The new admin suffers a direct, permanent loss of token0 and token1 equal to the full admin fee share outstanding at the time of the first post-transfer `collectPoolFees` call. The loss is bounded only by how much has accrued since the last collection; for active pools with non-zero `adminSpreadFeeE6` or `adminNotionalFeeE8`, this can be material.

---

### Likelihood Explanation

Admin transfers are an expected, documented lifecycle event (`proposePoolAdminTransfer` / `acceptPoolAdmin` are first-class factory functions). The old admin is the natural party with both motive and knowledge to front-run the new admin's `setPoolAdminFeeDestination` call by calling the permissionless `collectPoolFees` in the same block as `acceptPoolAdmin`. No special privilege is required beyond knowing the pool address.

---

### Recommendation

In `acceptPoolAdmin`, atomically reset `poolAdminFeeDestination[pool]` to the incoming admin's address (or to `address(0)` as a sentinel that blocks collection until the new admin sets a destination). Alternatively, add an overload of `acceptPoolAdmin` that accepts a `newFeeDestination` parameter and writes both mappings atomically:

```solidity
function acceptPoolAdmin(address pool) external override nonReentrant {
    address pending = pendingPoolAdmin[pool];
    if (pending == address(0)) revert NoPendingPoolAdminTransfer();
    if (msg.sender != pending) revert NotPendingPoolAdmin(pool, msg.sender, pending);
    address previousAdmin = poolAdmin[pool];
    poolAdmin[pool] = pending;
    delete pendingPoolAdmin[pool];
+   poolAdminFeeDestination[pool] = pending; // reset to new admin; they can update later
    emit PoolAdminTransferred(pool, previousAdmin, pending);
}
```

---

### Proof of Concept

```
Setup:
  pool deployed with oldAdmin, poolAdminFeeDestination = oldAdminWallet
  adminSpreadFeeE6 > 0, swaps occur → spread surplus accumulates

Step 1: oldAdmin calls proposePoolAdminTransfer(pool, newAdmin)
Step 2: newAdmin calls acceptPoolAdmin(pool)
        → poolAdmin[pool] = newAdmin
        → poolAdminFeeDestination[pool] still = oldAdminWallet  ← stale

Step 3: oldAdmin (or any MEV bot) calls collectPoolFees(pool)
        → collectFees(..., poolAdminFeeDestination[pool])
        → transferToken0(oldAdminWallet, adminShare0)   ← loss to newAdmin
        → transferToken1(oldAdminWallet, adminShare1)   ← loss to newAdmin

Step 4: newAdmin calls setPoolAdminFeeDestination(pool, newAdminWallet)
        → too late; fees already drained to oldAdminWallet

Alternatively, if newAdmin calls setPoolAdminFees before updating destination:
Step 3': newAdmin calls setPoolAdminFees(pool, ...)
         → internally calls collectFees(..., poolAdminFeeDestination[pool])
         → fees sent to oldAdminWallet even though newAdmin initiated the call
```

**Affected code:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

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

**File:** metric-core/contracts/MetricOmmPoolFactory.sol (L418-425)
```text
    IMetricOmmPoolCollectFees(pool)
      .collectFees(
        c.protocolSpreadFeeE6,
        c.adminSpreadFeeE6,
        c.protocolNotionalFeeE8,
        c.adminNotionalFeeE8,
        poolAdminFeeDestination[pool]
      );
```

**File:** metric-core/contracts/MetricOmmPoolFactory.sol (L518-526)
```text
  function acceptPoolAdmin(address pool) external override nonReentrant {
    address pending = pendingPoolAdmin[pool];
    if (pending == address(0)) revert NoPendingPoolAdminTransfer();
    if (msg.sender != pending) revert NotPendingPoolAdmin(pool, msg.sender, pending);
    address previousAdmin = poolAdmin[pool];
    poolAdmin[pool] = pending;
    delete pendingPoolAdmin[pool];
    emit PoolAdminTransferred(pool, previousAdmin, pending);
  }
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
