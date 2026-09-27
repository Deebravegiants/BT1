# [M] Front running in `matchOrders()`

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

Calls to `matchOrders()` are made to extract profit from the price difference between two opposite orders: left and right.


**code/contracts/exchange/contracts/src/MixinMatchOrders.sol:L106-L111**
```solidity
function matchOrders(
    LibOrder.Order memory leftOrder,
    LibOrder.Order memory rightOrder,
    bytes memory leftSignature,
    bytes memory rightSignature
)
```

The caller only pays protocol and transaction fees, so it's almost always profitable to front run every call to `matchOrders()`. That would lead to gas auctions and would make `matchOrders()` difficult to use.

#### Recommendation

Consider adding a commit-reveal scheme to `matchOrders()` to stop front running altogether.
