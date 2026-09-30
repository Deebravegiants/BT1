# [M] M-5 Lack of The Expiry Parameter

## Summary
Severity: Medium
Contest weight: 0.1119
Dataset id: 16461
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The issue arises within the OnchainLOB.sol#L199 function of the LOB contract.
There is an issue due to the absence of an expiration parameter for orders. Without this parameter, there is no guarantee that an order is added to the blockchain before a specified timestamp, which can be problematic if a transaction remains pending for a long time. This can lead to unintended execution of stale orders, potentially causing financial losses or market disruptions.
The issue is classified as medium severity because it affects the timing and validity of order execution, which can impact the reliability and efficiency of the trading platform.

## Recommendation
We recommend adding an expires parameter to the placeOrder function. This parameter should specify a timestamp before which the order must be added to the blockchain. If the transaction is executed after this timestamp, it should be reverted to ensure timely and valid order execution.
