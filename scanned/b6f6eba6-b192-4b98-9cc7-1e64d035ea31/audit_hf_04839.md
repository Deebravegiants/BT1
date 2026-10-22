# [M] Missing __Ownable_init() call in

## Summary
Severity: Medium
Contest weight: 0.3731
Dataset id: 22733
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
__Ownable_init() is not called in LenderCommitmentGroup_Smart::initialize(), which will make the contract not have any owner. LenderCommitmentGroup_Smart::initialize() does not call __Ownable_init() and will be left without owner. Inability to pause and unpause borrowing in LenderCommitmentGroup_Smart due to having no owner, as these functions are onlyOwner.

## Recommendation
Modify LenderCommitmentGroup_Smart::initialize() to call __Ownable_init():
```solidity
function initialize(
    ...
) external initializer returns (address poolSharesToken_) {
    __Ownable_init();
}
```
