# [M] Anyone can call `closeLoan`

## Summary
Severity: Medium
Contest weight: 0.4100
Dataset id: 1281
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[`MapleLoan.sol` L56-L63](https://github.com/maple-labs/loan/blob/9684bcef06481e493d060974b1777a4517c4e792/contracts/MapleLoan.sol#L56-L63)
```solidity
function closeLoan(uint256 amount_) external override returns (uint256 principal_, uint256 interest_) {
    // The amount specified is an optional amount to be transfer from the caller, as a convenience for EOAs.
    require(amount_ == uint256(0) || ERC20Helper.transferFrom(_fundsAsset, msg.sender, address(this), amount_), "ML:CL:TRANSFER_FROM_FAILED");

    ( principal_, interest_ ) = _closeLoan();

    emit LoanClosed(principal_, interest_);
}
```
Based on the context, we believe that the `closeLoan()` should only be called by the `borrower`. However, the current implementation allows anyone to call `closeLoan()` anytime after `fundLoan()`.

If there is no `earlyFee`, this enables a griefing attack, causing the `borrower` and `lender` to abandon this contract and redo everything which costs more gas.

If a platform fee exits, the lender will also suffer fund loss from the platform fee charged in `fundLoan()`.

## Recommendation
No recommendation
