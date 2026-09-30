# [M] GLOBAL-3 | Multiple Read-only Reenterancies

## Summary
Severity: Medium
Contest weight: 0.1287
Dataset id: 18509
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There are several instances where a user may gain control over the order execution tx before the
dataStore has been properly updated.
Firstly, in the SwapOrderUtils.swap function, the SwapUtils.swap is executed before the swap order
is removed from the dataStore. Since the swap can have shouldUnwrapNativeToken == true the
order.receiver will get called upon receiving the output of the swap.
Since native token transfers forward 200,000 gas (from the test environment) the receiver will have
ample gas to potentially exploit any system building on top of GMX V2 and relying on the swap order
in the dataStore.
Similarly in the OrderUtils.cancelOrder function, the orderVault.transferOut is executed before the
order is removed from the dataStore.

## Recommendation
In the SwapOrderUtils.swap function, remove the order with OrderStoreUtils.remove before the
SwapUtils.swap. And in the OrderUtils.cancelOrder function, remove the order with
OrderStoreUtils.remove before the orderVault.transferOut.
This way third parties building on top of GMX V2 cannot be exploited by the outdated order state in
these instances.
