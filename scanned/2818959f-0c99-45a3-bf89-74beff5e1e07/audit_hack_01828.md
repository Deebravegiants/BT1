# [C] Exchange - CancelOrder has no effect

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

The exchange provides means for the `trader` or `broker` to cancel the order. The `cancelOrder` method, however, only stores the hash of the canceled order in mapping but the mapping is never checked. It is therefore effectively impossible for a trader to cancel an order.

#### Examples


**code/contracts/exchange/Exchange.sol:L179-L187**
```solidity

function cancelOrder(LibOrder.Order memory order) public {
    require(msg.sender == order.trader || msg.sender == order.broker, "invalid caller");

    bytes32 orderHash = order.getOrderHash();
    cancelled[orderHash] = true;

    emit Cancel(orderHash);
}
```

#### Recommendation

* `matchOrders*` or `validateOrderParam` should check if `cancelled[orderHash] == true` and abort fulfilling the order. 
* Verify the order params (Signature) before accepting it as canceled.
