### Title
Pool Admin Bypasses `maxAdminSpreadFeeE6` Cap via Unchecked `setPoolBinAdditionalFees` — (`metric-core/contracts/MetricOmmPoolFactory.sol`)

---

### Summary

`MetricOmmPoolFactory` enforces `maxAdminSpreadFeeE6` on pool-level admin fees in `setPoolAdminFees`, but the sibling function `setPoolBinAdditionalFees` forwards per-bin fee values (`addFeeBuyE6`, `addFeeSellE6`) directly to the pool with **no cap check**, allowing the pool admin to charge traders fees that exceed the factory owner's intended ceiling.

---

### Finding Description

The factory defines a cap hierarchy for admin fees:

- `HARD_MAX_SPREAD_FEE_E6 = 200_000` (20%) — absolute ceiling set at construction.
- `maxAdminSpreadFeeE6` — owner-tunable cap, ≤ hard max, enforced in `setPoolAdminFees`.

`setPoolAdminFees` correctly enforces the cap: [1](#0-0) 

```solidity
if (newAdminSpreadFeeE6 > maxAdminSpreadFeeE6) revert AdminFeeTooHigh();
if (newAdminNotionalFeeE8 > maxAdminNotionalFeeE8) revert AdminFeeTooHigh();
```

However, `setPoolBinAdditionalFees` performs **no such check**: [2](#0-1) 

```solidity
function setPoolBinAdditionalFees(address pool, int8 bin, uint16 addFeeBuyE6, uint16 addFeeSellE6)
    external override nonReentrant onlyPoolAdmin(pool)
{
    IMetricOmmPoolFactoryActions(pool).setBinAdditionalFees(bin, addFeeBuyE6, addFeeSellE6);
}
```

The pool's `setBinAdditionalFees` only validates the bin index, not the fee magnitudes: [3](#0-2) 

These per-bin fees are then added directly to the base fee in every swap through that bin: [4](#0-3) 

```solidity
uint256 buyFeeX64 = baseFeeX64 + Math.mulDiv(binState.addFeeBuyE6, ONE_X64, 1e6);
uint256 sellFeeX64 = baseFeeX64 + Math.mulDiv(binState.addFeeSellE6, ONE_X64, 1e6);
```

`addFeeBuyE6` and `addFeeSellE6` are `uint16`, so they can reach **65,535** (≈ 6.55% in E6 units). The factory owner may set `maxAdminSpreadFeeE6` to any value from 0 to 200,000. If the owner sets it to, say, 1,000 (0.1%) to protect traders, the pool admin can still set per-bin fees to 65,535 (6.55%) — a **65× bypass** of the intended cap.

---

### Impact Explanation

Every swap routed through a bin with inflated `addFeeBuyE6`/`addFeeSellE6` pays fees far above the factory owner's cap. The excess fee is extracted from the trader's swap output (or inflated input), constituting a direct loss of user principal. The factory owner's cap mechanism — the primary protection against pool-admin fee abuse — is rendered ineffective for per-bin fees.

---

### Likelihood Explanation

The pool admin is a role assigned at pool creation and is semi-trusted. The factory owner's cap exists precisely because the pool admin is not fully trusted. Any pool admin (malicious or compromised) can call `setPoolBinAdditionalFees` at any time with no timelock, no cap check, and no factory-owner approval. The call path is short and requires no special setup beyond holding the pool admin role.

---

### Recommendation

Add a cap check in `setPoolBinAdditionalFees` mirroring the check in `setPoolAdminFees`:

```solidity
function setPoolBinAdditionalFees(address pool, int8 bin, uint16 addFeeBuyE6, uint16 addFeeSellE6)
    external override nonReentrant onlyPoolAdmin(pool)
{
    if (addFeeBuyE6  > maxAdminSpreadFeeE6) revert AdminFeeTooHigh();
    if (addFeeSellE6 > maxAdminSpreadFeeE6) revert AdminFeeTooHigh();
    IMetricOmmPoolFactoryActions(pool).setBinAdditionalFees(bin, addFeeBuyE6, addFeeSellE6);
}
```

Alternatively, introduce a dedicated `maxAdminBinFeeE6` cap so the factory owner can tune per-bin and pool-level limits independently.

---

### Proof of Concept

1. Factory owner deploys factory and sets `maxAdminSpreadFeeE6 = 1_000` (0.1%) via `setFeeCaps`.
2. Pool is created with a pool admin.
3. Pool admin calls `setPoolBinAdditionalFees(pool, 0, 65_535, 65_535)`.
4. No revert occurs — `addFeeBuyE6 = addFeeSellE6 = 65_535` is stored in `_binStates[0]`.
5. A trader swaps through bin 0. The effective fee is `baseFeeX64 + 65535/1e6 ≈ 6.55%` instead of the capped `0.1%`.
6. The trader receives ≈ 6.45% less output than the factory owner's cap permits, with the excess accruing as LP/admin spread fees.

### Citations

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

**File:** metric-core/contracts/MetricOmmPool.sol (L540-541)
```text
    uint256 buyFeeX64 = baseFeeX64 + Math.mulDiv(binState.addFeeBuyE6, ONE_X64, 1e6);
    uint256 sellFeeX64 = baseFeeX64 + Math.mulDiv(binState.addFeeSellE6, ONE_X64, 1e6);
```
