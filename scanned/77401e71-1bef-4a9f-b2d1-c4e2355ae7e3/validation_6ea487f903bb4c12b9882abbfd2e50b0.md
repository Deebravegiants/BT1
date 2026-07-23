### Title
`collectFees` DoS when `adminFeeDestination` is USDC-blacklisted, permanently blocking fee collection and fee-update admin flows — (File: metric-core/contracts/MetricOmmPool.sol)

---

### Summary

`MetricOmmPool.collectFees` uses a **push** pattern to transfer accrued spread and notional fees directly to `adminFeeDestination_`. If that address is USDC-blacklisted, every call to `collectFees` reverts. Because `MetricOmmPoolFactory.setPoolProtocolFee` and `setPoolAdminFees` both call `collectFees` as a mandatory first step before writing new fee parameters, a blacklisted `adminFeeDestination` simultaneously freezes all accrued protocol fees inside the pool **and** DoS-es the two factory functions that govern fee configuration.

---

### Finding Description

`MetricOmmPool.collectFees` (lines 416–427) unconditionally pushes tokens to `adminFeeDestination_`:

```solidity
if (totalFee0ToAdmin > 0) {
    transferToken0(adminFeeDestination_, totalFee0ToAdmin);   // ← push
}
if (totalFee1ToAdmin > 0) {
    transferToken1(adminFeeDestination_, totalFee1ToAdmin);   // ← push
}
if (totalFee0ToProtocol > 0) {
    transferToken0(FACTORY, totalFee0ToProtocol);
}
if (totalFee1ToProtocol > 0) {
    transferToken1(FACTORY, totalFee1ToProtocol);
}
notionalFeeToken0Scaled = 0;   // only reached if all transfers succeed
notionalFeeToken1Scaled = 0;
```

`adminFeeDestination_` is read from `poolAdminFeeDestination[pool]` in the factory and forwarded as a parameter. If the stored address is USDC-blacklisted, `safeTransfer` reverts, the entire call reverts, and the notional-fee accumulators are **never cleared**.

`MetricOmmPoolFactory.collectPoolFees` (lines 379–389) is callable by anyone and passes `poolAdminFeeDestination[pool]` directly into `collectFees`. It will revert for every caller.

`MetricOmmPoolFactory.setPoolProtocolFee` (lines 317–360) and `setPoolAdminFees` (lines 408–435) both call `collectFees` **before** writing the new fee configuration. If `collectFees` reverts, neither function can complete, so:

- The protocol owner cannot change protocol spread or notional fees.
- The pool admin cannot change admin spread or notional fees.

The state is fully rolled back on each revert, so no corruption occurs, but the fees remain locked inside the pool and the fee-management surface is completely frozen.

---

### Impact Explanation

**Direct loss of protocol fees**: Accrued spread surplus and notional fee accumulators cannot be extracted from the pool. The amounts grow with every swap but are inaccessible.

**Broken core admin functionality**: `setPoolProtocolFee` and `setPoolAdminFees` are the only on-chain paths to adjust fee rates. Both are DoS-ed, preventing the protocol from responding to market conditions (e.g., lowering fees to attract volume, or raising them to protect LPs).

Severity: **Medium** — fees are not permanently destroyed (they remain in the pool's balance), but they are inaccessible until the destination is changed, and the fee-update admin path is fully blocked in the interim.

---

### Likelihood Explanation

**Low** — USDC blacklisting of an `adminFeeDestination` address is an uncommon external event. However, the `adminFeeDestination` is an arbitrary address set by the pool admin; it could be a multisig, a DAO treasury, or any contract that USDC's issuer might later blacklist. The scenario is realistic for pools whose admin fee destination is a regulated or sanctioned entity.

---

### Recommendation

Replace the push pattern in `collectFees` with a **pull** (claim) pattern:

1. Accumulate admin and protocol fee amounts in per-token storage mappings keyed by destination address.
2. Expose a separate `claimFees(address token)` function that lets each destination withdraw its own balance.
3. `setPoolProtocolFee` and `setPoolAdminFees` can then snapshot/checkpoint the accrued amounts without executing any token transfer, eliminating the revert risk entirely.

This mirrors the standard recommendation for the original report and removes the dependency on the destination address being transfer-capable at the moment of fee collection or fee-rate update.

---

### Proof of Concept

1. Pool is deployed with `token0 = USDC`, `token1 = WETH`.
2. Pool admin sets `adminFeeDestination` to address `D` via `setPoolAdminFeeDestination`.
3. Swaps occur; spread surplus and notional fee accumulators grow.
4. USDC issuer blacklists `D`.
5. Anyone calls `MetricOmmPoolFactory.collectPoolFees(pool)`.
   - Factory calls `pool.collectFees(..., D)`.
   - Pool computes `totalFee0ToAdmin > 0`, calls `transferToken0(D, amount)`.
   - USDC `transfer` reverts (`D` is blacklisted).
   - `collectFees` reverts; `notionalFeeToken0Scaled` / `notionalFeeToken1Scaled` unchanged.
   - `collectPoolFees` reverts. ✗
6. Protocol owner calls `setPoolProtocolFee(pool, newFee, ...)`.
   - Internally calls `collectFees(...)` → same revert path.
   - Fee rate is **not** updated. ✗
7. Pool admin calls `setPoolAdminFees(pool, newFee, ...)`.
   - Same revert path. Fee rate **not** updated. ✗
8. All accrued fees remain locked in the pool. Fee configuration is frozen until the admin separately calls `setPoolAdminFeeDestination` to point to a non-blacklisted address, then retries collection. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

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

**File:** metric-core/contracts/MetricOmmPoolFactory.sol (L317-360)
```text
  /// @inheritdoc IMetricOmmPoolFactoryOwner
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
