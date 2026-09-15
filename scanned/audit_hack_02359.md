# [C] \[C02\] Orders cannot be cancelled

## Summary
Severity: Critical
Source: https://github.com/mcdexio/mai-protocol-v2/blob/4b198083ec4ae2d6851e101fc44ea333eaa3cd92/contracts/exchange/Exchange.sol#L180
Type: audit-issue

## Details
When a user or broker calls [cancelOrder](https://github.com/mcdexio/mai-protocol-v2/blob/4b198083ec4ae2d6851e101fc44ea333eaa3cd92/contracts/exchange/Exchange.sol#L180), [the cancelled mapping](https://github.com/mcdexio/mai-protocol-v2/blob/4b198083ec4ae2d6851e101fc44ea333eaa3cd92/contracts/exchange/Exchange.sol#L184) is updated, but this has no subsequent effects. In particular, [validateOrderParam](https://github.com/mcdexio/mai-protocol-v2/blob/4b198083ec4ae2d6851e101fc44ea333eaa3cd92/contracts/exchange/Exchange.sol#L155) does not check if the order has been cancelled.

Consider adding this check to the order validation to ensure cancelled orders cannot be filled.

**Update:** _Fixed. The validation now checks the cancellation status._
