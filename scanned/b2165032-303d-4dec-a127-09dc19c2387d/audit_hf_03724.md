# [M] Global position-fee-related state not updated until after liquidation checks are done

## Summary
Severity: Medium
Contest weight: 0.4111
Dataset id: 19851
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Global position-fee-related state not updated until after liquidation checks are done. Checking whether a position is liquidatable occurs before the global state is updated.

A position that should be liquidated in the current block, won't be liquidated until the next block, when the correct fee multipliers/factors are applied. A delayed liquidation means that a position that should have been liquidated will not be, likely causing a larger loss than should have been incurred.

State is updated after the liquidation checks:
```solidity
// File: gmx-synthetics/contracts/position/DecreasePositionUtils.sol : DecreasePositionUtils.decreasePosition()
if (BaseOrderUtils.isLiquidationOrder(params.order.orderType()) && !PositionUtils.isPositionLiquidatable(
    params.contracts.dataStore,
    params.contracts.referralStorage,
    params.position,
    params.market,
    cache.prices,
    true
)) {
    revert PositionShouldNotBeLiquidated();
}

PositionUtils.updateFundingAndBorrowingState(params, cache.prices);
```
cts/position/DecreasePositionUtils.sol#L152-L179

## Recommendation
Call PositionUtils.updateFundingAndBorrowingState() before all checks
