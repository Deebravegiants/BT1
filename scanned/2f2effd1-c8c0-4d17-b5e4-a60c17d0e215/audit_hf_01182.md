# [M] Anyone can cause DoS of the distributeTokens method

## Summary
Severity: Medium
Contest weight: 0.1098
Dataset id: 5059
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The distributeTokens method of the Agent contract transfers each share of the agent token distribution to the corresponding contributor using ERC-20 transfers in a for-loop. Since the maximum number of contributors (length of the contributors storage array) is unbounded, the for-loop might exceed the block gas limit due to the costly transfers.

Impact Explanation:  
High: DoS of the distributeTokens method once the for-loop of agent token transfers exceeds the block gas limit if the contributors array is too large. Consequently, the main use case of the protocol will be dysfunctional and agent tokens become stuck in the contract.

## Recommendation
It is recommended to implement a pull pattern where contributors have to manually call a method to claim their corresponding share of the agent token distribution instead of having it automatically transferred to them in the distributeTokens method.
