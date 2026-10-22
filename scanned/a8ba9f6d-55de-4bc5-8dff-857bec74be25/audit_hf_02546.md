# [M] Missing validation of orderCounts in RebalancingLib.previewRebalancingOrders() can make rebalancing stuck

## Summary
Severity: Medium
Contest weight: 0.4229
Dataset id: 13553
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The StartRebalancingParams struct that is passed to RebalancingLib.previewRebalancingOrders() contains an orderCounts array that specifies the number of orders for all the chains in the current (old) anatomy. If params.orderCounts[vars.chainIndex] turns out to be too small, RebalancingLib._createOrders() will try to access an out-of-bounds index and revert. This is not an issue. If on the other hand params.orderCounts[vars.chainIndex] is greater than the actual number of orders created, the chainOrders struct contains empty orders with all fields at the default zero value.
```solidity
struct OrderId {
    Currency sellCurrency = 0;
    Currency localBuyCurrency = 0;
    Currency finalDestinationBuyCurrency = 0;
    uint256 finalDestinationChainId = 0;
}
```
The empty orders will be received on the remote chain, where the call to RemoteOmnichainMessenger._injectLocalBuyCurrency() inside RemoteOmnichainMessenger.pushOrders() will revert since there is no bridging info for finalDestinationChainId = 0. This is a vulnerability that needs to be fixed since by front-running the rebalancing, a user can influence the amount of orders created.

## Recommendation
The solution incurs some overhead as the number of orders is only known once the last chain has been iterated over. All prior chains can have new orders until the last call to RebalancingLib._createOrders() has been executed. It is possible to iterate over all orders from chainOrders[0] to chainOrders[vars.orderIndex-1] and ensure that chainOrders[i].orders.length == vars.counters[i].
