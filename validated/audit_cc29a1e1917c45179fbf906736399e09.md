### Title
Pool Admin Can Instantly Set Uncapped Bin Additional Fees to Frontrun Swaps — (`metric-core/contracts/MetricOmmPoolFactory.sol` / `metric-core/contracts/MetricOmmPool.sol`)

---

### Summary

The pool admin can call `setPoolBinAdditionalFees()` to instantly change per-bin buy/sell fees (`addFeeBuyE6` / `addFeeSellE6`) with no upper-bound cap and no timelock. This is a direct analog to M-26: a malicious (or accidentally mistaken) pool admin can frontrun a pending user swap by spiking the bin fee to `type(uint16).max` (65 535 = 6.5535% in E6 units), causing the trader to receive far fewer tokens than expected, with the excess retained as LP fees.

---

### Finding Description

`MetricOmmPoolFactory.setPoolBinAdditionalFees()` passes the caller-supplied `addFeeBuyE6` / `addFeeSellE6` values directly to the pool with **no cap validation** and **no timelock**:

```solidity
// MetricOmmPoolFactory.sol L450-457
function setPoolBinAdditionalFees(address pool, int8 bin, uint16 addFeeBuyE6, uint16 addFeeSellE6)
    external
    override
    nonReentrant
    onlyPoolAdmin(pool)
{
    IMetricOmmPoolFactoryActions(pool).setBinAdditionalFees(bin, addFeeBuyE6, addFeeSellE6);
}
```

The pool's `setBinAdditionalFees()` performs only a bin-index range check before writing:

```solidity
// MetricOmmPool.sol L464-474
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

These per-bin fees are added directly to the oracle-derived base fee at swap execution time:

```solidity
// MetricOmmPool.sol L910, L999
params.baseFeeX64 + Math.mulDiv(binState.addFeeBuyE6, ONE_X64, 1e6)
```

The effective fee applied to a swap is therefore `baseFee + addFeeBuyE6/1e6`, and the bin additional component can be set to `65535/1e6 ≈ 6.55%` instantly, with no prior notice to users.

**Contrast with `setPoolAdminFees()`**, which enforces explicit caps before writing:

```solidity
// MetricOmmPoolFactory.sol L414-415
if (newAdminSpreadFeeE6 > maxAdminSpreadFeeE6) revert AdminFeeTooHigh();
if (newAdminNotionalFeeE8 > maxAdminNotionalFeeE8) revert AdminFeeTooHigh();
```

No equivalent guard exists for bin additional fees.

---

### Impact Explanation

A trader submitting a swap against the current bin receives fewer output tokens than the oracle price and their `priceLimitX64` slippage tolerance would suggest, because the effective execution fee is silently elevated. The excess input value is retained inside the bin as LP balance, benefiting LPs (including the pool admin if they are also an LP) at the trader's expense. This is a **direct loss of user principal** on every swap that crosses the manipulated bin.

Maximum extractable additional fee per swap: `65535 / 1e6 ≈ 6.55%` of the swap notional, applied on top of the oracle spread fee.

---

### Likelihood Explanation

The pool admin is a semi-trusted role that can act unilaterally and atomically. No timelock, no governance delay, and no cap guard stands between the admin and the fee change. A malicious admin can observe a large pending swap in the mempool and frontrun it in the same block. Even a non-malicious admin who raises fees for legitimate reasons can accidentally frontrun a user whose transaction was already in flight.

---

### Recommendation

1. **Add a hard cap** on `addFeeBuyE6` and `addFeeSellE6` in `setPoolBinAdditionalFees()`, analogous to `maxAdminSpreadFeeE6` / `maxAdminNotionalFeeE8` already enforced for pool-level admin fees.
2. **Add a timelock** (or at minimum a two-step propose/execute pattern) for bin additional fee changes, consistent with the timelock already applied to price-provider updates (`proposePoolPriceProvider` / `executePoolPriceProviderUpdate`).

Example fix in `MetricOmmPoolFactory.setPoolBinAdditionalFees()`:

```solidity
if (addFeeBuyE6 > maxAdminBinFeeE6) revert AdminFeeTooHigh();
if (addFeeSellE6 > maxAdminBinFeeE6) revert AdminFeeTooHigh();
```

---

### Proof of Concept

1. Pool is live; `curBinIdx = 0`; `addFeeBuyE6 = 0` (no additional fee).
2. User submits `swap(recipient, false, 1_000e18, priceLimitX64, ...)` — buying token0 with token1.
3. Pool admin observes the pending transaction and frontruns with:
   ```solidity
   factory.setPoolBinAdditionalFees(pool, 0, 65535, 65535);
   ```
4. User's swap executes with effective fee = `baseFee + 0.065535`, paying ~6.55% more token1 than expected for the same token0 output (exact-output) or receiving ~6.55% fewer token0 (exact-input).
5. The extra token1 retained in the bin accrues to LPs; the user has no recourse. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

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

**File:** metric-core/contracts/MetricOmmPool.sol (L906-914)
```text
          (curPosInBinCache, delta0Scaled, delta1Scaled, binLpFeeAmountScaled) = SwapMath.buyToken0InBinSpecifiedOut(
            binState,
            curPosInBinCache,
            state,
            params.baseFeeX64 + Math.mulDiv(binState.addFeeBuyE6, ONE_X64, 1e6),
            lowerPriceX64,
            upperPriceX64,
            params.priceLimitX64,
            spreadFeeE6
```
