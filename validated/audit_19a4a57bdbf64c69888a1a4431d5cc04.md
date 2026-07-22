### Title
Pool Admin Can Set Uncapped Per-Bin Additional Fees, Bypassing the Protocol Fee Cap System - (File: metric-core/contracts/MetricOmmPoolFactory.sol)

---

### Summary

`setPoolBinAdditionalFees` allows the pool admin to set per-bin additional spread fees (`addFeeBuyE6`, `addFeeSellE6`) with no upper-bound validation. Every other fee-setting path in the factory enforces a hard cap, but this path is silently exempt, letting a pool admin push the effective per-bin fee above the protocol's hard ceiling.

---

### Finding Description

The factory enforces a two-tier fee cap hierarchy:

- **Hard constants** (immutable): `HARD_MAX_SPREAD_FEE_E6 = 200_000` (20 %) and `HARD_MAX_NOTIONAL_FEE_E8 = 1_000_000`.
- **Owner-settable caps**: `maxAdminSpreadFeeE6` ≤ `HARD_MAX_SPREAD_FEE_E6`.
- **Pool-admin path** (`setPoolAdminFees`): enforces `newAdminSpreadFeeE6 > maxAdminSpreadFeeE6 → revert AdminFeeTooHigh`. [1](#0-0) [2](#0-1) 

However, the parallel pool-admin path `setPoolBinAdditionalFees` contains **no cap check at all**:

```solidity
function setPoolBinAdditionalFees(address pool, int8 bin, uint16 addFeeBuyE6, uint16 addFeeSellE6)
    external
    override
    nonReentrant
    onlyPoolAdmin(pool)
{
    IMetricOmmPoolFactoryActions(pool).setBinAdditionalFees(bin, addFeeBuyE6, addFeeSellE6);
}
``` [3](#0-2) 

The parameters are typed `uint16`, so the maximum settable value is `65_535` (≈ 6.55 % in E6 units). These values are described in the interface as fees applied **on top of the base spread**:

> `addFeeBuyE6` — Additional buy-side spread fee in E6 on top of base spread. [4](#0-3) 

Because the base spread fee is already allowed up to `HARD_MAX_SPREAD_FEE_E6 = 200_000` (20 %), adding an uncapped bin-level fee on top produces a total effective fee of up to **200_000 + 65_535 = 265_535 E6 (≈ 26.55 %)** for any single bin — 33 % above the hard ceiling the protocol advertises.

---

### Impact Explanation

A pool admin can silently raise the effective swap cost for any specific bin beyond the protocol's hard cap. Traders routing through that bin pay more than the maximum fee the protocol guarantees, directly reducing the token amount they receive. Because the bin additional fee is additive to the base spread fee and is not reflected in the `maxAdminSpreadFeeE6` / `HARD_MAX_SPREAD_FEE_E6` guards, the cap invariant is broken for any pool whose admin sets a non-zero bin additional fee. This constitutes a direct loss of swap output for users and an admin-boundary break where the pool admin exceeds the protocol-enforced fee ceiling.

---

### Likelihood Explanation

The pool admin is a semi-trusted role whose fee-setting power is explicitly bounded by the factory's cap system. Any pool admin — including one who turns adversarial after deployment — can call `setPoolBinAdditionalFees` at any time with `addFeeBuyE6 = type(uint16).max` without any on-chain resistance. No timelock, no owner approval, and no cap check stands in the way.

---

### Recommendation

Add the same cap enforcement to `setPoolBinAdditionalFees` that exists in `setPoolAdminFees`. Define a hard constant (e.g., `HARD_MAX_BIN_ADDITIONAL_FEE_E6`) and revert if either parameter exceeds it, ensuring the sum of base spread fee and bin additional fee cannot exceed `HARD_MAX_SPREAD_FEE_E6`:

```solidity
function setPoolBinAdditionalFees(address pool, int8 bin, uint16 addFeeBuyE6, uint16 addFeeSellE6)
    external
    override
    nonReentrant
    onlyPoolAdmin(pool)
{
    if (addFeeBuyE6 > maxAdminSpreadFeeE6) revert AdminFeeTooHigh();
    if (addFeeSellE6 > maxAdminSpreadFeeE6) revert AdminFeeTooHigh();
    IMetricOmmPoolFactoryActions(pool).setBinAdditionalFees(bin, addFeeBuyE6, addFeeSellE6);
}
```

---

### Proof of Concept

1. Factory owner deploys a pool with `maxAdminSpreadFeeE6 = 200_000` (20 %) and `spreadFeeE6 = 200_000`.
2. Pool admin calls:
   ```solidity
   factory.setPoolBinAdditionalFees(pool, 0, 65_535, 65_535);
   ```
   No revert occurs — `setPoolBinAdditionalFees` has no cap check.
3. A trader swaps through bin 0. The effective spread fee applied is `200_000 + 65_535 = 265_535 E6` (≈ 26.55 %), exceeding the protocol's hard cap of 20 % (`HARD_MAX_SPREAD_FEE_E6 = 200_000`).
4. The trader receives fewer tokens than the protocol's fee ceiling permits, with no on-chain mechanism to prevent or detect the violation. [3](#0-2) [1](#0-0)

### Citations

**File:** metric-core/contracts/MetricOmmPoolFactory.sol (L44-45)
```text
  uint24 internal constant HARD_MAX_SPREAD_FEE_E6 = 200_000;
  uint24 internal constant HARD_MAX_NOTIONAL_FEE_E8 = 1_000_000;
```

**File:** metric-core/contracts/MetricOmmPoolFactory.sol (L414-415)
```text
    if (newAdminSpreadFeeE6 > maxAdminSpreadFeeE6) revert AdminFeeTooHigh();
    if (newAdminNotionalFeeE8 > maxAdminNotionalFeeE8) revert AdminFeeTooHigh();
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

**File:** metric-core/contracts/interfaces/IMetricOmmPool/IMetricOmmPoolFactoryActions.sol (L52-56)
```text
  /// @notice Set per-bin additional buy and sell spread fees in E6 on top of base spread.
  /// @param bin Bin index within the pool configured bin range.
  /// @param addFeeBuyE6 Additional fee on buys into the bin (E6).
  /// @param addFeeSellE6 Additional fee on sells out of the bin (E6).
  function setBinAdditionalFees(int8 bin, uint16 addFeeBuyE6, uint16 addFeeSellE6) external;
```
