### Title
Pool Admin Bypasses `maxAdminSpreadFeeE6` Cap via Uncapped Per-Bin Additional Fees - (`metric-core/contracts/MetricOmmPoolFactory.sol`)

### Summary
`setPoolBinAdditionalFees` forwards per-bin fee values to the pool with **no cap validation**, allowing the pool admin to charge effective swap fees that exceed the `maxAdminSpreadFeeE6` boundary enforced on the global admin spread fee.

### Finding Description
The factory enforces a tiered fee cap system. The factory owner sets `maxAdminSpreadFeeE6` (up to the hard ceiling of 20%) to bound what the pool admin may charge via `setPoolAdminFees`. That function correctly validates:

```solidity
// MetricOmmPoolFactory.sol:414-415
if (newAdminSpreadFeeE6 > maxAdminSpreadFeeE6) revert AdminFeeTooHigh();
if (newAdminNotionalFeeE8 > maxAdminNotionalFeeE8) revert AdminFeeTooHigh();
```

However, `setPoolBinAdditionalFees` passes `addFeeBuyE6` and `addFeeSellE6` straight through with **no cap check**:

```solidity
// MetricOmmPoolFactory.sol:450-457
function setPoolBinAdditionalFees(address pool, int8 bin, uint16 addFeeBuyE6, uint16 addFeeSellE6)
    external override nonReentrant onlyPoolAdmin(pool)
{
    IMetricOmmPoolFactoryActions(pool).setBinAdditionalFees(bin, addFeeBuyE6, addFeeSellE6);
}
```

The pool's `setBinAdditionalFees` only validates the bin index, not the fee magnitudes:

```solidity
// MetricOmmPool.sol:464-474
function setBinAdditionalFees(int8 bin, uint16 addFeeBuyE6, uint16 addFeeSellE6)
    external onlyFactory nonReentrant(PoolActions.SET_BIN_ADDITIONAL_FEES)
{
    if (bin < LOWEST_BIN || bin > HIGHEST_BIN) revert InvalidBinIndex(bin);
    BinState storage s = _binStates[bin];
    s.addFeeBuyE6 = addFeeBuyE6;
    s.addFeeSellE6 = addFeeSellE6;
    emit BinAdditionalFeesUpdated(bin, addFeeBuyE6, addFeeSellE6);
}
```

These per-bin fees are then **added on top of the base spread fee** during every swap in `getSellAndBuyPrices` and the internal swap path:

```solidity
// MetricOmmPool.sol:540-544
uint256 buyFeeX64 = baseFeeX64 + Math.mulDiv(binState.addFeeBuyE6, ONE_X64, 1e6);
uint256 sellFeeX64 = baseFeeX64 + Math.mulDiv(binState.addFeeSellE6, ONE_X64, 1e6);

uint256 askBeforeNotional = Math.mulDiv(marginalPriceX64, ONE_X64 + buyFeeX64, ONE_X64, Math.Rounding.Ceil);
uint256 bidAfterSpread = Math.mulDiv(marginalPriceX64, ONE_X64, ONE_X64 + sellFeeX64, Math.Rounding.Floor);
```

`addFeeBuyE6` and `addFeeSellE6` are `uint16`, so the pool admin can set them to any value up to 65 535 (≈ 6.55 % in E6 terms) per bin. Because these are additive to the base spread fee, the effective per-bin fee can exceed `maxAdminSpreadFeeE6` by up to 6.55 percentage points — with no factory-level guard preventing it.

### Impact Explanation
The factory owner's `maxAdminSpreadFeeE6` cap is the primary mechanism protecting users from excessive admin-side fees. The pool admin can silently bypass this cap for any active bin by calling `setPoolBinAdditionalFees(pool, curBinIdx, 65535, 65535)`. Traders executing swaps in that bin pay a higher effective fee than the cap permits, with the excess going to the pool (and ultimately collectible by the admin via fee collection). This is a direct, quantifiable loss of user funds relative to the fee boundary the factory owner intended to enforce.

### Likelihood Explanation
The pool admin is a semi-trusted role with explicitly defined boundaries (fee caps, pause levels, timelock-gated oracle rotation). The per-bin fee path is the only admin-accessible fee setter that skips cap validation. Any pool admin who wants to extract more than `maxAdminSpreadFeeE6` can do so immediately, in a single transaction, for any bin, without the factory owner's knowledge or consent.

### Recommendation
Add cap validation inside `setPoolBinAdditionalFees` before forwarding to the pool:

```solidity
function setPoolBinAdditionalFees(address pool, int8 bin, uint16 addFeeBuyE6, uint16 addFeeSellE6)
    external override nonReentrant onlyPoolAdmin(pool)
{
    if (addFeeBuyE6 > maxAdminSpreadFeeE6) revert AdminFeeTooHigh();
    if (addFeeSellE6 > maxAdminSpreadFeeE6) revert AdminFeeTooHigh();
    IMetricOmmPoolFactoryActions(pool).setBinAdditionalFees(bin, addFeeBuyE6, addFeeSellE6);
}
```

Alternatively, enforce the combined cap (global spread fee + per-bin fee) against `maxAdminSpreadFeeE6` to prevent the total effective fee from exceeding the intended ceiling.

### Proof of Concept
1. Factory owner deploys factory with `maxAdminSpreadFeeE6 = 50_000` (5 %).
2. Pool admin calls `setPoolAdminFees(pool, 50_000, 0)` — accepted, at the cap.
3. Pool admin calls `setPoolBinAdditionalFees(pool, 0, 65535, 65535)` — **no revert**.
4. A trader swaps in bin 0: effective buy/sell fee = 5 % (base) + 6.55 % (per-bin) = **11.55 %**, more than double the intended cap.
5. The excess fee accrues inside the pool and is swept to the admin fee destination via `collectPoolFees`. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** metric-core/contracts/MetricOmmPoolFactory.sol (L413-415)
```text
  {
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

**File:** metric-core/contracts/MetricOmmPool.sol (L540-544)
```text
    uint256 buyFeeX64 = baseFeeX64 + Math.mulDiv(binState.addFeeBuyE6, ONE_X64, 1e6);
    uint256 sellFeeX64 = baseFeeX64 + Math.mulDiv(binState.addFeeSellE6, ONE_X64, 1e6);

    uint256 askBeforeNotional = Math.mulDiv(marginalPriceX64, ONE_X64 + buyFeeX64, ONE_X64, Math.Rounding.Ceil);
    uint256 bidAfterSpread = Math.mulDiv(marginalPriceX64, ONE_X64, ONE_X64 + sellFeeX64, Math.Rounding.Floor);
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
