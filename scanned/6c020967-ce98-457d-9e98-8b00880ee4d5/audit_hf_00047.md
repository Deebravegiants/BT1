# [H] DIEM-4 | Users Can Avoid Borrowing Fees

## Summary
Severity: High
Contest weight: 0.2377
Dataset id: 123
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When users pay borrowing fees, the current interest rate is computed from the IVXLP contract and projected across the period from [trade.timestamp, block.timestamp]. However the interest rate is variable and will not have been this same value for that entire period. Users can update their positions when the interest rate drops to lock in the lower rate for the [trade.timestamp, block.timestamp] period, even though the interest rate was in fact higher during the majority of that period. As the interest rate is dependent on the utilized collateral, a malicious actor can wait until another trader closes their isBuy == true trade and decreases the interest rate to then update their own trade to lock in the lower rate. Additionally, a malicious actor could front-run other user’s who are closing their trades and increase the interest rate to cause grief.

## Recommendation
Refactor the method used to track borrowing fees, such as a per-size approach: Trades are marked with an initial borrowingFeePerSize and upon closing a trade the borrowing fees are computed as the delta between the trade’s latestBorrowingFeePerSize and the current borrowingFeePerSize. The borrowingFeePerSize is updated according to the previous interest rate over the previous period whenever the interest rate is changed.
