# [H] Cross available value is not accounting the fees

## Summary
Severity: High
Contest weight: 0.6371
Dataset id: 22910
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
Cross available value is the maximum margin that an account can open a position. This value currently subtracts if the account has any losses but does not account for fees, which can be negative as well. This makes the account have a greater maximum margin than it should be.

Cross available value is calculated in AccountProcess::getCrossAvailableValue() function as follows:
(totalNetValue + cache.totalIMUsd + accountProps.orderHoldInUsd).toInt256() -
totalUsedValue.toInt256() +
(cache.totalPnl >= 0 ? int256(0) : cache.totalPnl) -
(cache.totalIMUsdFromBalance + totalBorrowingValue).toInt256();
```

As we can observe in the above code snippet, if there is a negative PnL, it is subtracted from the position's available cross value. The reason for this is that if the account has a negative PnL, that means when the position is realized, the account's net value will drop. Hence, it is critical to account for anything that can/will drop the account's net value, such as the sum PnL of the positions the account has. However, this calculation is missing a key factor that can also drop the account's net value: the fees — closeFee, borrowingFee, and fundingFee. When the position is settled, these fees will be added on top of the PnL, so it can be assumed that they will affect the user's latest settled margin.

Textual PoC: Assume an account has:  
totalNetValue = 200  
cache.totalIMUsd = 100  
totalUsedValue = 100  
totalBorrowingValue = 100  
totalIMUsdFromBalance = 0  
totalPnl = 0  
totalFees = 20

The cross available value for this account would be:  
(200 + 100 + 0) - 100 + 0 - (0 + 100) = 100

This means that the account can open another position with a margin of 100. However, there are 20 fees to pay, which if the account would close the position, the account would have 80 cross available value. In an extreme case, if the fees are very high (say 80), the account can open a position while it is actually eligible for liquidations.

Another case would be the account withdrawing the cross available value, which is 100$ worth of collateral, although the position is already in -20$, which will make the position not fully collateralized.

Users can open positions with a greater margin than their actual total balance. Hence, high.

## Recommendation
Add the fees just like the PnL. If it's negative (funding fees), then don't add it; if it's positive, subtract it from the total value.
