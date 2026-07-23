### Title
Pool Admin Bypasses `maxAdminSpreadFeeE6` Cap via `setPoolBinAdditionalFees` — (File: `metric-core/contracts/MetricOmmPoolFactory.sol`)

---

### Summary

`MetricOmmPoolFactory.setPoolBinAdditionalFees` forwards per-bin additional fee values directly to the pool with no validation against the factory's `maxAdminSpreadFeeE6` cap. When the factory owner reduces that cap below `uint16.max` (65 535), the pool admin can still push per-bin fees up to 65 535 (≈ 6.55 % in E6 units), silently exceeding the owner-imposed ceiling and overcharging every trader who crosses the affected bin.

---

### Finding Description

The factory enforces two separate fee-cap paths for the pool admin:

**`setPoolAdminFees` — cap enforced:** [1](#0-0) 

```solidity
if (newAdminSpreadFeeE6 > maxAdminSpreadFeeE6) revert AdminFeeTooHigh();
if (newAdminNotionalFeeE8 > maxAdminNotionalFeeE8) revert AdminFeeTooHigh();
```

**`setPoolBinAdditionalFees` — no cap check:** [2](#0-1) 

```solidity
function setPoolBinAdditionalFees(address pool, int8 bin, uint16 addFeeBuyE6, uint16 addFeeSellE6)
    external override nonReentrant onlyPoolAdmin(pool)
{
    IMetricOmmPoolFactoryActions(pool).setBinAdditionalFees(bin, addFeeBuyE6, addFeeSellE6);
}
```

The pool-level `setBinAdditionalFees` also performs no cap check — it only validates the bin index: [3](#0-2) 

The per-bin fee fields are `uint16` (max 65 535), while `maxAdminSpreadFeeE6` is a `uint24` that the factory owner can lower at any time via `setFeeCaps`: [4](#0-3) 

The hard ceiling is `HARD_MAX_SPREAD_FEE_E6 = 200_000`, but the owner can reduce `maxAdminSpreadFeeE6` to any value ≥ 0. Once it is set below 65 535, the pool admin can still write per-bin fees up to 65 535 through `setPoolBinAdditionalFees`, bypassing the reduced cap entirely.

The `BinState` struct confirms both fields are `uint16`: [5](#0-4) 

---

### Impact Explanation

Every swap that crosses a bin with inflated `addFeeBuyE6` / `addFeeSellE6` pays a higher spread fee than the factory owner's cap permits. The excess fee accrues to the pool and is later split between the admin and protocol via `collectPoolFees`, meaning the pool admin extracts more value from traders than the governance-imposed ceiling allows. This is a direct, per-swap loss of user principal routed to the admin.

---

### Likelihood Explanation

The bypass is always latent. It becomes exploitable the moment the factory owner lowers `maxAdminSpreadFeeE6` below 65 535 — a routine governance action (e.g., capping admin fees at 1 % = 10 000 E6). The pool admin then calls `setPoolBinAdditionalFees` with values up to 65 535, which is 6.5× the intended ceiling. No special timing, flash loan, or external oracle condition is required; the pool admin's normal operational key is sufficient.

---

### Recommendation

Add the same cap guard to `setPoolBinAdditionalFees` that exists in `setPoolAdminFees`:

```solidity
function setPoolBinAdditionalFees(
    address pool, int8 bin, uint16 addFeeBuyE6, uint16 addFeeSellE6
) external override nonReentrant onlyPoolAdmin(pool) {
    if (addFeeBuyE6  > maxAdminSpreadFeeE6) revert AdminFeeTooHigh();
    if (addFeeSellE6 > maxAdminSpreadFeeE6) revert AdminFeeTooHigh();
    IMetricOmmPoolFactoryActions(pool).setBinAdditionalFees(bin, addFeeBuyE6, addFeeSellE6);
}
```

Alternatively, introduce a dedicated `maxAdminBinSpreadFeeE6` cap (also `uint16`-bounded) so the factory owner can tune per-bin limits independently of the global admin spread cap.

---

### Proof of Concept

1. Factory owner deploys factory; `maxAdminSpreadFeeE6` starts at `200_000`.
2. Factory owner calls `setFeeCaps(200_000, 10_000, 1_000_000, 1_000_000)` to cap admin spread at 1 % (10 000 E6).
3. Pool admin calls `setPoolAdminFees(pool, 15_000, 0)` → reverts `AdminFeeTooHigh` ✓ (cap enforced).
4. Pool admin calls `setPoolBinAdditionalFees(pool, 0, 65_535, 65_535)` → **succeeds** (no cap check).
5. Bin 0 now carries `addFeeBuyE6 = 65_535` ≈ 6.55 %, far above the 1 % cap the owner intended.
6. Every trader whose swap crosses bin 0 pays 6.55 % extra spread; the excess accrues to the admin. [6](#0-5) [2](#0-1)

### Citations

**File:** metric-core/contracts/MetricOmmPoolFactory.sol (L284-315)
```text
  function setFeeCaps(
    uint24 newMaxProtocolSpreadFeeE6,
    uint24 newMaxAdminSpreadFeeE6,
    uint24 newMaxProtocolNotionalFeeE8,
    uint24 newMaxAdminNotionalFeeE8
  ) external override onlyOwner {
    if (
      newMaxProtocolSpreadFeeE6 > HARD_MAX_SPREAD_FEE_E6 || newMaxAdminSpreadFeeE6 > HARD_MAX_SPREAD_FEE_E6
        || newMaxProtocolNotionalFeeE8 > HARD_MAX_NOTIONAL_FEE_E8 || newMaxAdminNotionalFeeE8 > HARD_MAX_NOTIONAL_FEE_E8
    ) {
      revert FeeCapsExceedHardLimit();
    }
    maxProtocolSpreadFeeE6 = newMaxProtocolSpreadFeeE6;
    maxAdminSpreadFeeE6 = newMaxAdminSpreadFeeE6;
    maxProtocolNotionalFeeE8 = newMaxProtocolNotionalFeeE8;
    maxAdminNotionalFeeE8 = newMaxAdminNotionalFeeE8;

    if (spreadProtocolFeeE6 > newMaxProtocolSpreadFeeE6) {
      uint24 oldFeeE6 = spreadProtocolFeeE6;
      spreadProtocolFeeE6 = newMaxProtocolSpreadFeeE6;
      emit SpreadProtocolFeeDefaultUpdated(oldFeeE6, newMaxProtocolSpreadFeeE6);
    }
    if (protocolNotionalFeeE8 > newMaxProtocolNotionalFeeE8) {
      uint24 oldFeeE8 = protocolNotionalFeeE8;
      protocolNotionalFeeE8 = newMaxProtocolNotionalFeeE8;
      emit ProtocolNotionalFeeDefaultUpdated(oldFeeE8, newMaxProtocolNotionalFeeE8);
    }

    emit FeeCapsUpdated(
      newMaxProtocolSpreadFeeE6, newMaxAdminSpreadFeeE6, newMaxProtocolNotionalFeeE8, newMaxAdminNotionalFeeE8
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

**File:** metric-core/contracts/MetricOmmPoolFactory.sol (L450-457)
```text
  function setPoolBinAdditionalFees(address pool, int8 bin, uint16 addFeeBuyE6, uint16 addFeeSellE6)
    external
    override
    nonReentrant
    onlyPoolAdmin(pool)
  {
    IMetricOmmPoolFactoryActions(pool).setBinAdditionalFees(bin, addFeeBuyE6, addFeeSellE6);
  }
```

**File:** metric-core/contracts/MetricOmmPool.sol (L464-474)
```text
  function setBinAdditionalFees(int8 bin, uint16 addFeeBuyE6, uint16 addFeeSellE6)
    external
    onlyFactory
    nonReentrant(PoolActions.SET_BIN_ADDITIONAL_FEES)
  {
    if (bin < LOWEST_BIN || bin > HIGHEST_BIN) revert InvalidBinIndex(bin);
    BinState storage s = _binStates[bin];
    s.addFeeBuyE6 = addFeeBuyE6;
    s.addFeeSellE6 = addFeeSellE6;
    emit BinAdditionalFeesUpdated(bin, addFeeBuyE6, addFeeSellE6);
  }
```

**File:** metric-core/contracts/types/PoolStorage.sol (L19-25)
```text
struct BinState {
  uint104 token0BalanceScaled;
  uint104 token1BalanceScaled;
  uint16 lengthE6;
  uint16 addFeeBuyE6;
  uint16 addFeeSellE6;
}
```
