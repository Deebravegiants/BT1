# [H] MJR-1 It is possible to process a non-existing array element or skip an

## Summary
Severity: High
Contest weight: 0.0326
Dataset id: 16480
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
At the line Strategy.sol#L424 is working with the elements of the _newPositions array in a loop. For each element of the lenders array, there must be an element of the _newPositions array. But now the iteration of elements for the _newPositions array is not done correctly. This will cause the manualAllocation() function to work incorrectly.

## Recommendation
It is necessary to correct the index value for the _newPositions array: if (address(lenders[j]) == _newPositions[i].lender) {
