Audit Report

## Title
Pool Admin Can Set Uncapped Per-Bin Additional Fees, Bypassing the Global Spread Fee Hard Cap - (File: metric-core/contracts/MetricOmmPoolFactory.sol)

## Summary
`setPoolBinAdditionalFees` forwards caller-supplied `addFeeBuyE6` / `addFeeSellE6` values directly to `MetricOmmPool.setBinAdditionalFees` with no upper-bound check, while the parallel `setPoolAdminFees` path enforces `maxAdminSpreadFeeE6`. A pool admin can set per-bin additional fees to `type(uint16).max` (65 535, i.e. 6.5535% in E6 units), silently exceeding the factory-owner-controlled hard cap on every swap touching that bin.

## Finding Description
`setPoolAdminFees` correctly gates admin fee changes: [1](#0-0) 

But `setPoolBinAdditionalFees` passes values through with no cap check: [2](#0-1) 

`MetricOmmPool.setBinAdditionalFees` only validates the bin index, not the fee magnitudes: [3](#0-2) 

The uncapped values are then added directly to `baseFeeX64` on every swap: [4](#0-3) [5](#0-4) 

`BinState` stores both fields as `uint16`, so the maximum settable value is 65 535: [6](#0-5) 

The factory owner's hard cap is enforced only on global spread fees via `setFeeCaps`: [7](#0-6) 

There is no code path that applies `maxAdminSpreadFeeE6` or `HARD_MAX_SPREAD_FEE_E6` to per-bin additional fees, either at set-time or at swap-time.

## Impact Explanation
A pool admin sets `addFeeBuyE6 = 65535` on the active bin. Every trader buying token0 through that bin pays an extra 6.5535% on top of the oracle-derived base fee. The surplus accrues inside the bin as LP balance, effectively transferring trader principal to LPs under admin control. This is a direct, quantifiable loss of user funds on every swap touching that bin, and constitutes an admin-boundary break: the pool admin exceeds the spread fee cap the factory owner established via `setFeeCaps`. This matches the allowed impact gate: "Admin-boundary break: pool admin exceeds caps."

## Likelihood Explanation
The pool admin role is explicitly semi-trusted — the protocol caps global admin fees precisely because it does not fully trust pool admins. Any pool admin, including one that turns adversarial after deployment, can call `setPoolBinAdditionalFees` at any time with no timelock, no prior fee collection step, and no additional guard beyond `onlyPoolAdmin(pool)`. The call is a single transaction with no preconditions other than holding the pool admin role.

## Recommendation
Add a cap check inside `setPoolBinAdditionalFees` mirroring the pattern used for global admin fees:

```solidity
function setPoolBinAdditionalFees(address pool, int8 bin, uint16 addFeeBuyE6, uint16 addFeeSellE6)
    external override nonReentrant onlyPoolAdmin(pool)
{
    if (addFeeBuyE6  > maxAdminSpreadFeeE6) revert AdminFeeTooHigh();
    if (addFeeSellE6 > maxAdminSpreadFeeE6) revert AdminFeeTooHigh();
    IMetricOmmPoolFactoryActions(pool).setBinAdditionalFees(bin, addFeeBuyE6, addFeeSellE6);
}
```

Alternatively, introduce a dedicated `maxBinAdditionalFeeE6` storage variable, enforce it here, and also validate it in `_unpackAndValidateBinStates` at pool creation time.

## Proof of Concept
```
1. Factory owner deploys pool with maxAdminSpreadFeeE6 = 200_000 (20%).
2. Pool admin calls:
       factory.setPoolBinAdditionalFees(pool, 0, 65535, 65535);
   No revert — the value is never compared against maxAdminSpreadFeeE6.
3. Trader calls pool.swap(recipient, false, -1e18, ...).
   Inside the swap loop, the effective buy fee becomes:
       baseFeeX64 + mulDiv(65535, ONE_X64, 1e6)
   ≈ oracle_spread_fee + 6.5535%
4. Trader receives ~6.5% fewer tokens than the oracle price implies.
   The surplus stays in the bin, accruing to LPs under admin control.
5. The factory owner's hard cap is silently exceeded with no on-chain revert.
```

### Citations

**File:** metric-core/contracts/MetricOmmPoolFactory.sol (L290-295)
```text
    if (
      newMaxProtocolSpreadFeeE6 > HARD_MAX_SPREAD_FEE_E6 || newMaxAdminSpreadFeeE6 > HARD_MAX_SPREAD_FEE_E6
        || newMaxProtocolNotionalFeeE8 > HARD_MAX_NOTIONAL_FEE_E8 || newMaxAdminNotionalFeeE8 > HARD_MAX_NOTIONAL_FEE_E8
    ) {
      revert FeeCapsExceedHardLimit();
    }
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

**File:** metric-core/contracts/MetricOmmPool.sol (L469-473)
```text
    if (bin < LOWEST_BIN || bin > HIGHEST_BIN) revert InvalidBinIndex(bin);
    BinState storage s = _binStates[bin];
    s.addFeeBuyE6 = addFeeBuyE6;
    s.addFeeSellE6 = addFeeSellE6;
    emit BinAdditionalFeesUpdated(bin, addFeeBuyE6, addFeeSellE6);
```

**File:** metric-core/contracts/MetricOmmPool.sol (L910-910)
```text
            params.baseFeeX64 + Math.mulDiv(binState.addFeeBuyE6, ONE_X64, 1e6),
```

**File:** metric-core/contracts/MetricOmmPool.sol (L1177-1177)
```text
              params.baseFeeX64 + Math.mulDiv(binState.addFeeSellE6, ONE_X64, 1e6),
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
