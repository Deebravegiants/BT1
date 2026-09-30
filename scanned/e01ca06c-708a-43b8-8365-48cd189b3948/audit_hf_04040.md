# [H] At claimDefaulted, the lender may not receive

## Summary
Severity: High
Contest weight: 0.7258
Dataset id: 20472
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function claimDefaulted(uint256 loanID_) external returns (uint256, uint256, uint256) {
    Loan memory loan = loans[loanID_];
    delete loans[loanID_];
```

Loan data is deletead in claimDefaulted function. loan.unclaimed is not checked before data deletead. So, if claimDefaulted is called while there are unclaimed tokens, the lender will not be able to get the unclaimed tokens. Lender cannot get unclaimed token.

## Recommendation
Process unclaimed tokens before deleting loan data.
```solidity
function claimDefaulted(uint256 loanID_) external returns (uint256, uint256, uint256) {
    claimRepaid(loanID_);
    Loan memory loan = loans[loanID_];
    delete loans[loanID_];
}
```
