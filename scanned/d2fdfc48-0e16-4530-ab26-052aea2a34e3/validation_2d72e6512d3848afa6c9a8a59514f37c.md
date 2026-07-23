### Title
Pool Admin Bypasses `maxAdminSpreadFeeE6` Cap via Uncapped Per-Bin Additional Fees — (File: `metric-core/contracts/MetricOmmPoolFactory.sol`)

### Summary

`setPoolBinAdditionalFees` passes `addFeeBuyE6`/`addFeeSellE6` directly to the pool with no cap validation, while the parallel `setPoolAdminFees` path explicitly enforces `maxAdminSpreadFeeE6`. A pool admin can set per-bin fees to `type(uint16).max` (65 535 E6 ≈ 6.55 %) on every bin, stacking that uncapped surcharge on top of the already-capped global spread fee and the oracle spread, causing swappers to receive materially less output than the protocol's fee-cap system is designed to allow.

### Finding Description

`MetricOmmPoolFactory.setPoolAdminFees` enforces the admin spread cap before updating the pool:

```solidity
// MetricOmmPoolFactory.sol lines 414-415
if (newAdminSpreadFeeE6 > maxAdminSpreadFeeE6) revert AdminFeeTooHigh();
if (newAdminNotionalFeeE8 > maxAdminNotionalFeeE8) revert AdminFeeTooHigh();
``` [1](#0-0) 

`setPoolBinAdditionalFees`, by contrast, performs no such check — it forwards the caller-supplied `uint16` values straight to the pool:

```solidity
// MetricOmmPoolFactory.sol lines 450-457
function setPoolBinAdditionalFees(address pool, int8 bin, uint16 addFeeBuyE6, uint16 addFeeSellE6)
  external override nonReentrant onlyPoolAdmin(pool)
{
  IMetricOmmPoolFactoryActions(pool).setBinAdditionalFees(bin, addFeeBuyE6, addFeeSellE6);
}
``` [2](#0-1) 

The pool's `setBinAdditionalFees` stores the values without any cap check either: [3](#0-2) 

During every swap, the per-bin fee is added directly to the oracle-derived base fee before computing the execution price:

```solidity
// MetricOmmPool.sol line 541
uint256 sellFeeX64 = baseFeeX64 + Math.mulDiv(binState.addFeeSellE6, ONE_X64, 1e6);
// MetricOmmPool.sol line 910
params.baseFeeX64 + Math.mulDiv(binState.addFeeBuyE6, ONE_X64, 1e6)
``` [4](#0-3) [5](#0-4) 

The hard cap for admin spread is `HARD_MAX_SPREAD_FEE_E6 = 200_000` (20 %). The `uint16` ceiling for per-bin fees is 65 535 E6 ≈ 6.55 %. These are independent additive layers: a pool admin can simultaneously hold the global spread fee at the 20 % cap **and** set per-bin fees to 65 535 on every bin, producing an effective per-bin fee of ≈ 26.55 % — 6.55 percentage points above the hard cap — with no on-chain guard preventing it.

### Impact Explanation

Every swap routed through a bin whose `addFeeBuyE6`/`addFeeSellE6` has been set to `type(uint16).max` pays an extra ≈ 6.55 % surcharge on top of the oracle spread and the capped global spread fee. The excess is retained in the pool's spread surplus and collected by the admin via `collectPoolFees`. Swappers receive materially less output than the protocol's fee-cap architecture is designed to permit. This is a direct, quantifiable loss of swap output for every affected trade.

### Likelihood Explanation

The pool admin role is semi-trusted: any address can create a pool and designate itself admin. A malicious or compromised pool admin can call `setPoolBinAdditionalFees` in a single transaction with no timelock, no prior announcement, and no on-chain resistance. The asymmetry between the capped `setPoolAdminFees` path and the uncapped `setPoolBinAdditionalFees` path makes this trivially exploitable by any pool admin who chooses to act adversarially.

### Recommendation

Add a cap check in `MetricOmmPoolFactory.setPoolBinAdditionalFees` mirroring the check in `setPoolAdminFees`:

```solidity
function setPoolBinAdditionalFees(address pool, int8 bin, uint16 addFeeBuyE6, uint16 addFeeSellE6)
  external override nonReentrant onlyPoolAdmin(pool)
{
  if (addFeeBuyE6  > maxAdminSpreadFeeE6) revert AdminFeeTooHigh();
  if (addFeeSellE6 > maxAdminSpreadFeeE6) revert AdminFeeTooHigh();
  IMetricOmmPoolFactoryActions(pool).setBinAdditionalFees(bin, addFeeBuyE6, addFeeSellE6);
}
```

Alternatively, introduce a dedicated `maxBinAdditionalFeeE6` cap (settable by the factory owner within the hard limit) so that per-bin fees can be governed independently but still bounded.

### Proof of Concept

1. Pool admin calls:
   ```solidity
   factory.setPoolAdminFees(pool, maxAdminSpreadFeeE6, 0); // global fee at hard cap (20 %)
   factory.setPoolBinAdditionalFees(pool, 0, type(uint16).max, type(uint16).max); // +6.55 % per-bin, no revert
   ```
2. A swapper calls `pool.swap(...)` routing through bin 0.
3. Inside `_executeSwap`, the effective fee applied is:
   ```
   feeX64 = baseFeeX64 (oracle spread)
           + mulDiv(65535, ONE_X64, 1e6)   // ≈ 6.55 % extra, uncapped
   ```
   plus the global `spreadFeeE6` (20 %) applied separately.
4. The swapper's output is reduced by the uncapped 6.55 % surcharge; the excess accumulates in the pool's spread surplus and is swept to the admin via `collectPoolFees`. [6](#0-5) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** metric-core/contracts/MetricOmmPoolFactory.sol (L44-45)
```text
  uint24 internal constant HARD_MAX_SPREAD_FEE_E6 = 200_000;
  uint24 internal constant HARD_MAX_NOTIONAL_FEE_E8 = 1_000_000;
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

**File:** metric-core/contracts/MetricOmmPool.sol (L539-548)
```text

    uint256 buyFeeX64 = baseFeeX64 + Math.mulDiv(binState.addFeeBuyE6, ONE_X64, 1e6);
    uint256 sellFeeX64 = baseFeeX64 + Math.mulDiv(binState.addFeeSellE6, ONE_X64, 1e6);

    uint256 askBeforeNotional = Math.mulDiv(marginalPriceX64, ONE_X64 + buyFeeX64, ONE_X64, Math.Rounding.Ceil);
    uint256 bidAfterSpread = Math.mulDiv(marginalPriceX64, ONE_X64, ONE_X64 + sellFeeX64, Math.Rounding.Floor);

    uint256 nf = notionalFeeE8;
    buyPriceX64 = Math.mulDiv(askBeforeNotional, 1e8, 1e8 - nf, Math.Rounding.Ceil).toUint128();
    sellPriceX64 = Math.mulDiv(bidAfterSpread, 1e8 - nf, 1e8, Math.Rounding.Floor).toUint128();
```

**File:** metric-core/contracts/MetricOmmPool.sol (L906-915)
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
          );
```
