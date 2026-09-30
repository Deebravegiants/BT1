# [M] Lenders will lose everything if they get removed

## Summary
Severity: Medium
Contest weight: 0.3807
Dataset id: 6072
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function withdraw(uint128 amount) external override onlyRole(LENDER_ROLE) {
    // ...
}

function claim() external override onlyRole(LENDER_ROLE) {
    // ...
}
```
The issue arises because the Agreement Factory has the ability to remove any lender's role without restriction. If a lender is removed from the LENDER_ROLE, they lose access to both their deposited funds and any rewards, since they can no longer call withdraw or claim.

## Recommendation
Consider decoupling access control from fund ownership. One approach is to allowing them to call withdraw and claim even if they are removed. If the need to actually freeze the funds we can introduce a blacklist functionality which can then blacklist a lender for accessing his funds or rewards.
