# [M] M-12 | Resetting Does Not Refund Tokens

## Summary
Severity: Medium
Contest weight: 0.1667
Dataset id: 1986
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a user calls withdrawRequestRedeem(), if their balance after is less than minimumCollateral then resetTransaction() will set their pending amount to zero. However, totalPendingWithdrawals will only be decremented by the amount of shares the user passes in. This will lead to totalPendingWithdrawals being larger than the actual amount that is intended to be withdrawn. A malicious user could continuously call requestRedeem() in conjunction with withdrawRequestRedeem in order to inflate totalPendingWithdrawals to be larger than collateralFromPreviousEpoch plus totalPendingDeposits. This will cause a DoS via underflow when _reconcilePendingTransactions() is called. Additionally, when a user calls withdrawRequestDeposit(), totalPendingDeposits is only decremented by assets. This will lead to the user’s remaining tokens to be donated to other users of the protocol.

## Proof of Concept
https://github.com/GuardianAudits/foil-2/compare/rd2-remediations...POC_DOS_MIN_COLLAT?expand=1#diff-4fe03eaa0c5a23c3854772730dd5ca9a0a7de11d8d7e4394a623f6cf2b5496e5

## Recommendation
If the user’s remaining amount is less than the minimumCollateral, then decrement totalPendingWithdrawals by the full amount or refund the remainder of their balance before calling resetTransaction(), depending on if it is a redeem or deposit.
