# [M] EmptyFeedPrice will cause orders to be can-

## Summary
Severity: Medium
Contest weight: 0.4071
Dataset id: 19838
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In most cases where orders are submitted using invalid oracle prices, the check for
isEmptyPriceError() returns true, and the order execution is allowed to revert,
rather than canceling the order.
EmptyFeedPrice isn't counted as one of these errors, and so if the price reaches
zero, any outstanding order will be canceled.
Orders to close positions will be canceled, leading to losses.
Only isEmptyPriceError() errors are allowed to revert:
```solidity
// File: gmx-synthetics/contracts/exchange/OrderHandler.sol :
OrderHandler._handleOrderError()
    if (
        OracleUtils.isEmptyPriceError(errorSelector) ||
        errorSelector == InvalidKeeperForFrozenOrder.selector
    ) {
        ErrorUtils.revertWithCustomError(reasonBytes);
    }
    Order.Props memory order = OrderStoreUtils.get(dataStore, key);
    bool isMarketOrder =
        BaseOrderUtils.isMarketOrder(order.orderType());

    if (isMarketOrder) {
        OrderUtils.cancelOrder(
```
Other orders get frozen or canceled

## Recommendation
Include EmptyFeedPrice in the list of OracleUtils.isEmptyPriceError() errors
