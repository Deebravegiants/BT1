# [H] ORDH-1 | Keeper Griefed With orderUpdatedAtBlock

## Summary
Severity: High
Contest weight: 0.2553
Dataset id: 18873
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Orders will remain in the order store when the OracleBlockNumbersAreSmallerThanRequired error occurs during execution. Therefore a malicious user can cause the keeper to continuously expend gas to attempt to execute an order without requiring any additional executionFee. Consider the following scenario: A malicious user frontrun’s the keepers execution tx and updates their order, updating the orderUpdatedAtBlock. Now the keeper's tx goes through all of the price setting and order execution logic up to the oracle block number validation. Then the order execution tx reverts, the keeper has spent a significant amount of gas but the order still remains, with the same executionFee still attached. The malicious user may continue to do this and continue to gas grief the keeper. The malicious user can then cancel their order at any time to receive their executionFee back. The scenario can be exacerbated with an order that requires many prices to be set where the malicious user includes a maximum length swapPath that requires many prices.

## Recommendation
Require a non-refundable WNT payment upon order updates to disincentivize such attacks. Otherwise consider validating the oracle block numbers for the order early on in the order execution to minimize the amount of gas that can be wasted.
