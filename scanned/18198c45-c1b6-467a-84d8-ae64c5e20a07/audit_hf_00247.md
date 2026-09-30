# [H] `makePayment`

## Summary
Severity: High
Contest weight: 0.5704
Dataset id: 1280
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[`MapleLoan.sol` L86-L93](https://github.com/maple-labs/loan/blob/9684bcef06481e493d060974b1777a4517c4e792/contracts/MapleLoan.sol#L86-L93)
```solidity
function makePayment(uint256 amount_) external override returns (uint256 principal_, uint256 interest_) {
    // The amount specified is an optional amount to be transfer from the caller, as a convenience for EOAs.
    require(amount_ == uint256(0) || ERC20Helper.transferFrom(_fundsAsset, msg.sender, address(this), amount_), "ML:MP:TRANSFER_FROM_FAILED");

    ( principal_, interest_ ) = _makePayment();

    emit PaymentMade(principal_, interest_);
}
```
The current implementation allows anyone to call `makePayment()` and repay the loan with `_drawableFunds`.

This makes it possible for a malicious `lender` to call `makePayment()` multiple times right after `fundLoan()` and retrieve most of the funds back immediately, while then `borrower` must continue to make payments or lose the `collateral`.

## Recommendation
No recommendation
