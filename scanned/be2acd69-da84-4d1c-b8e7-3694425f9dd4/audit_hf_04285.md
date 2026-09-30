# [H] H-01 | Borrowing Fees Increase Based On Incorrect Rate

## Summary
Severity: High
Contest weight: 0.3138
Dataset id: 21424
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a position is updated the updateFundingAndBorrowingState function is called which updates CUMULATIVE_BORROWING_FACTOR based on the recent rate as well as the time since the last update. The rate of which the CUMULATIVE_BORROWING_FACTOR will increase is dependent on what percentage of the pools liquidity is being borrowed. The higher the percentage the higher the rate. By updating the CUMULATIVE_BORROWING_FACTOR before any changes to the state that could affect rate the borrowing fees can correctly be calculated. The issue however is that this is not the case everywhere. When a user withdraws or deposits they will change the rate. As they withdraw the rate will increase and as they deposit the rate will decrease. However because the CUMULATIVE_BORROWING_FACTOR is not updated before a deposit/withdraw, the next time it is updated the rate will use the new value not the value that was actually representative of the elapsed time. Leading to excessive fees being charged if a withdraw occurs, or insufficient fees being charged if a deposit occurs. With protocols integrating into GMX large deposits or withdraws will occur which will have a larger impact on the inaccuracy of the fees. The excessive fees being charged would lead to near liquidateable positions to become unexpectedly pushed to a liquidateable state. This step-wise jump in borrowing fees can also lead to arbitrage opportunities where attackers can profit off the inaccurate jump by making timely orders and deposits.

## Recommendation
Update the Funding and Borrowing state early in the executeDeposit and executeWithdrawal functions.
