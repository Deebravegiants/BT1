# [H] H-02 | Incorrect Positions Removed

## Summary
Severity: High
Contest weight: 0.1917
Dataset id: 2410
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the executeOrderByKeeper function the executablePositionIds list is populated with the indexes of each position tick range before any modifications have been made to the positionTickRangeList. However in the _handleKeeperExecuteCallback function the ids are removed sequentially, thereby adjusting the indexes of some positions after each removal and invalidating the provided executablePositionIds. This will end up in the wrong positions being removed from the executablePositionIds list. This will only be avoided if the keeper provides a carefully ordered list to the executeOrderByKeeper function which is in such an order that the removal of each iterative position does not affect the index of each subsequent one.

## Recommendation
Consider reading the most up to date index of each position directly before removing it in the _handleKeeperExecuteCallback for loop.
