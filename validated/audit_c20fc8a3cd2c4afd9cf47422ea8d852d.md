Audit Report

## Title
Pool Admin Bypasses `maxAdminSpreadFeeE6` Cap via Uncapped Per-Bin Additional Fees - (`metric-core/contracts/MetricOmmPoolFactory.sol`)

## Summary
`setPoolBinAdditionalFees` forwards `addFeeBuyE6` and `addFeeSellE6` to the pool with no validation against `maxAdminSpreadFeeE6`, while `setPoolAdminFees` correctly enforces that cap. Because per-bin fees are added on top of the base spread fee during every swap, a pool admin can set per-bin fees up to 65 535 (≈ 6.55 % in E6 terms) per bin, causing the effective swap fee to exceed the factory-owner-imposed ceiling by up to 6.55 percentage points. Traders in affected bins pay more than the cap permits, with the excess accruing to the admin.

## Finding Description
`setPoolAdminFees` enforces the cap at `MetricOmmPoolFactory.sol` L414–415:

```solidity
if (newAdminSpreadFeeE6 > maxAdminSpreadFeeE6) revert AdminFeeTooHigh();
if (newAdminNotionalFeeE8 > maxAdminNotionalFeeE8) revert AdminFeeTooHigh();
```

`setPoolBinAdditionalFees` at L450–457 performs no equivalent check before forwarding to the pool:

```solidity
function setPoolBinAdditionalFees(address pool, int8 bin, uint16 addFeeBuyE6, uint16 addFeeSellE6)
    external override nonReentrant onlyPoolAdmin(pool)
{
    IMetricOmmPoolFactoryActions(pool).setBinAdditionalFees(bin, addFeeBuyE6, addFeeSellE6);
}
```

`setBinAdditionalFees` in `MetricOmmPool.sol` at L464–474 only validates the bin index, writing the unchecked values directly into `BinState.addFeeBuyE6` / `addFeeSellE6` (both `uint16`, max 65 535).

During every swap, `getSellAndBuyPrices` at L540–541 adds these per-bin fees on top of `baseFeeX64`:

```solidity
uint256 buyFeeX64  = baseFeeX64 + Math.mulDiv(binState.addFeeBuyE6,  ONE_X64, 1e6);
uint256 sellFeeX64 = baseFeeX64 + Math.mulDiv(binState.addFeeSellE6, ONE_X64, 1e6);
```

The resulting ask/bid prices at L543–544 embed the full combined fee, so traders pay the uncapped total. The excess fee accrues inside the pool and is collectible by the admin via `collectPoolFees`.

## Impact Explanation
This is a direct admin-boundary break: the pool admin exceeds the `maxAdminSpreadFeeE6` cap set by the factory owner, which is the primary mechanism protecting traders from excessive admin-side fees. Traders executing swaps in any bin where per-bin fees are set above zero suffer a quantifiable, direct loss of funds relative to the fee ceiling the factory owner intended to enforce. The excess is not refundable and flows to the admin fee destination.

## Likelihood Explanation
The pool admin is explicitly semi-trusted within defined caps and timelocks. The per-bin fee setter is the only admin-accessible fee path that skips cap validation. Any pool admin can exploit this in a single transaction (`setPoolBinAdditionalFees(pool, binIdx, 65535, 65535)`) for any active bin, immediately and without the factory owner's knowledge or consent. No special preconditions beyond holding the pool admin role are required.

## Recommendation
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

Alternatively, enforce the combined cap (global spread fee + per-bin fee ≤ `maxAdminSpreadFeeE6`) to prevent the total effective fee from exceeding the intended ceiling.

## Proof of Concept
1. Factory owner deploys factory with `maxAdminSpreadFeeE6 = 50_000` (5 %).
2. Pool admin calls `setPoolAdminFees(pool, 50_000, 0)` — accepted, at the cap.
3. Pool admin calls `setPoolBinAdditionalFees(pool, 0, 65535, 65535)` — no revert; `BinState.addFeeBuyE6` and `addFeeSellE6` are set to 65 535.
4. A trader swaps in bin 0: effective buy/sell fee = 5 % (base) + 6.55 % (per-bin) = **11.55 %**, more than double the intended cap.
5. The excess fee accrues inside the pool and is swept to the admin fee destination via `collectPoolFees`.