# [H] ORDM-4 | Execution Fee May Be Circumvented

## Summary
Severity: High
Contest weight: 0.5531
Dataset id: 20576
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The current execution fee process only charges the user if the user-supplied order specifies a non-zero execution fee.
```solidity
if (_order.executionFee != 0) {
    _chargeExecutionFee(orderId, market.depositToken, _order.executionFee, _order.userAddress);
}
```
Because there is no requirement that the execution fee must be non-zero, a user has no incentive to pass a non-zero execution fee and pay extra for their order. As a result, keepers will not be properly remunerated for settling orders and liquidations. This can lead to grieving as the protocol must pay a fee each time the oracle price is updated, in addition to the gas needed for execution.

## Recommendation
Create a state variable for the execution fee and validate that it matches the execution fee passed on the order.
