# [M] Unsafe implementation of `fundLoan`

## Summary
Severity: Medium
Contest weight: 0.4333
Dataset id: 1282
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[`MapleLoanInternals.sol` L257-L273](https://github.com/maple-labs/loan/blob/9684bcef06481e493d060974b1777a4517c4e792/contracts/MapleLoanInternals.sol#L257-L273)
```solidity
uint256 treasuryFee = (fundsLent_ * ILenderLike(lender_).treasuryFee() * _paymentInterval * _paymentsRemaining) / uint256(365 days * 10_000);

// Transfer delegate fee, if any, to the pool delegate, and decrement drawable funds.
uint256 delegateFee = (fundsLent_ * ILenderLike(lender_).investorFee() * _paymentInterval * _paymentsRemaining) / uint256(365 days * 10_000);

// Drawable funds is the amount funded, minus any fees.
_drawableFunds = fundsLent_ - treasuryFee - delegateFee;

require(
    treasuryFee == uint256(0) || ERC20Helper.transfer(_fundsAsset, ILenderLike(lender_).mapleTreasury(), treasuryFee),
    "MLI:FL:T_TRANSFER_FAILED"
);

require(
    delegateFee == uint256(0) || ERC20Helper.transfer(_fundsAsset, ILenderLike(lender_).poolDelegate(), delegateFee),
    "MLI:FL:PD_TRANSFER_FAILED"
);
```
In the current implementation, `mapleTreasury`, `poolDelegate` and `treasuryFee` are taken from user input `lender_`, which can be faked by setting up a contract with `ILenderLike` interfaces.

This allows the attacker to set very high fees, making `_drawableFunds` near 0.

Since `mapleTreasury` and `poolDelegate` are also read from `lender_`, `treasuryFee` and `investorFee` can be retrieved back to the attacker.

As a result, the borrower won’t get any `_drawableFunds` while also being unable to remove collateral.

## Recommendation
No recommendation
