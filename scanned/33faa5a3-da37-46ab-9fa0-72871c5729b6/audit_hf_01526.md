# [M] getBidValue() is not always used

## Summary
Severity: Medium
Contest weight: 0.3771
Dataset id: 8074
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Sorter uses getBidValue() to sort the bids. However Atlas / _bidFindingIteration() and escrow / _getBidAmount() don't do that and use solverOp.bidAmount directly. In the example code these values are the same because the following function is used. However in the general case they might be different.
```solidity
function getBidValue(SolverOperation calldata solverOp) public pure override returns (uint256) {
    return solverOp.bidAmount;
}
```

## Recommendation
Also use getBidValue() in Atlas / _bidFindingIteration() and escrow / _getBidAmount(), or if the use is limited remove it from Sorter to be consistent.
