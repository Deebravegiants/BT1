### Title
`setPoolAdminFeeDestination` Redirects Accrued Admin Fees to New Destination Without Prior Collection — (`metric-core/contracts/MetricOmmPoolFactory.sol`)

---

### Summary

`MetricOmmPoolFactory.setPoolAdminFeeDestination()` updates `poolAdminFeeDestination[pool]` without first flushing accrued admin fees to the old destination. Every subsequent `collectPoolFees()` call passes the **new** destination to `pool.collectFees()`, permanently redirecting fees that were earned under the old destination. The old fee recipient loses all uncollected admin fees.

---

### Finding Description

The factory maintains two parallel "collect-before-change" patterns for fee-rate mutations, but omits the flush step for the destination mutation.

`setPoolAdminFees` (the fee-rate setter) correctly collects first: [1](#0-0) 

```solidity
function setPoolAdminFees(...) external nonReentrant onlyPoolAdmin(pool) {
    ...
    PoolFeeConfig memory c = poolFeeConfig[pool];
    IMetricOmmPoolCollectFees(pool).collectFees(
        c.protocolSpreadFeeE6, c.adminSpreadFeeE6,
        c.protocolNotionalFeeE8, c.adminNotionalFeeE8,
        poolAdminFeeDestination[pool]   // ← flushes to OLD destination first
    );
    c.adminSpreadFeeE6 = newAdminSpreadFeeE6;
    ...
}
```

`setPoolAdminFeeDestination` (the destination setter) does **not**: [2](#0-1) 

```solidity
function setPoolAdminFeeDestination(address pool, address newAdminFeeDestination)
    external override nonReentrant onlyPoolAdmin(pool)
{
    if (newAdminFeeDestination == address(0)) revert InvalidAdminFeeDestination();
    poolAdminFeeDestination[pool] = newAdminFeeDestination;   // ← no flush
    emit PoolAdminFeeDestinationUpdated(pool, newAdminFeeDestination);
}
```

`collectPoolFees` (permissionless) always reads the **current** mapping value and forwards it to the pool: [3](#0-2) 

```solidity
function collectPoolFees(address pool) external override nonReentrant {
    PoolFeeConfig memory c = poolFeeConfig[pool];
    IMetricOmmPoolCollectFees(pool).collectFees(
        c.protocolSpreadFeeE6, c.adminSpreadFeeE6,
        c.protocolNotionalFeeE8, c.adminNotionalFeeE8,
        poolAdminFeeDestination[pool]   // ← now points to NEW destination
    );
}
```

The pool's `collectFees` interface accepts `adminFeeDestination` as a caller-supplied parameter and transfers tokens directly to it: [4](#0-3) 

There is no on-pool record of the old destination; once the mapping is overwritten, the accrued-but-uncollected admin fee balance is irrecoverably redirected.

---

### Impact Explanation

All admin fees that accrued between the last `collectPoolFees` call and the `setPoolAdminFeeDestination` call are transferred to the **new** destination on the next collection. The old destination — which may be a separate treasury, DAO, or multisig — receives nothing for that period. This is a direct, permanent loss of owed token balances with no recovery path.

Severity: **Medium** (direct loss of owed admin fees; bounded by the uncollected accrual window, but no cap exists on that window).

---

### Likelihood Explanation

- The pool admin can call `setPoolAdminFeeDestination` at any time with no timelock.
- `collectPoolFees` is permissionless, so the pool admin can sequence the two calls atomically in a single transaction to maximise the stolen window.
- The old fee destination has no on-chain mechanism to force a prior flush.
- The scenario is reachable by any pool admin whose fee destination is a distinct entity (e.g., a DAO treasury separate from the admin multisig).

---

### Recommendation

Mirror the pattern used in `setPoolAdminFees` and `setPoolProtocolFee`: flush accrued fees to the **old** destination before overwriting the mapping.

```diff
function setPoolAdminFeeDestination(address pool, address newAdminFeeDestination)
    external override nonReentrant onlyPoolAdmin(pool)
{
    if (newAdminFeeDestination == address(0)) revert InvalidAdminFeeDestination();
+   // Flush accrued fees to the current (old) destination before rotating.
+   PoolFeeConfig memory c = poolFeeConfig[pool];
+   IMetricOmmPoolCollectFees(pool).collectFees(
+       c.protocolSpreadFeeE6, c.adminSpreadFeeE6,
+       c.protocolNotionalFeeE8, c.adminNotionalFeeE8,
+       poolAdminFeeDestination[pool]
+   );
    poolAdminFeeDestination[pool] = newAdminFeeDestination;
    emit PoolAdminFeeDestinationUpdated(pool, newAdminFeeDestination);
}
```

---

### Proof of Concept

1. Pool is live; spread and notional fees have been accruing for N blocks. Old destination = `oldDest`.
2. Pool admin calls `setPoolAdminFeeDestination(pool, newDest)` — no flush occurs; `poolAdminFeeDestination[pool]` is now `newDest`.
3. Anyone (or the pool admin) calls `collectPoolFees(pool)`.
4. Factory reads `poolAdminFeeDestination[pool]` → `newDest` and passes it to `pool.collectFees(...)`.
5. All accrued admin-share tokens (both token0 and token1) are transferred to `newDest`.
6. `oldDest` receives zero tokens for the entire accrual period, despite being the entitled recipient.

The pool admin can execute steps 2–3 atomically, guaranteeing the maximum possible fee theft in a single block.

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

**File:** metric-core/contracts/interfaces/IMetricOmmPool/IMetricOmmPoolCollectFees.sol (L27-33)
```text
  function collectFees(
    uint256 protocolSpreadFeeE6,
    uint256 adminSpreadFeeE6,
    uint256 protocolNotionalFeeE8,
    uint256 adminNotionalFeeE8,
    address adminFeeDestination
  ) external;
```
