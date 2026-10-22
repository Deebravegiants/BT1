# [H] Admin Can Overcharge Users Due to Incorrect Fee Application in FundContract

## Summary
Severity: High
Contest weight: 0.2467
Dataset id: 8718
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The FundContract incorrectly applies management fees instead of trading fees during withdrawals, leading to users being overcharged. The issue arises in the _withdraw() function, where the sharesTradingFee is incorrectly calculated as (_shares * userWithdraw.managementFee) / userWithdraw, instead of using the trading fee stored in the user’s withdrawal data.  
Additionally, the trading fee is not properly set during withdrawal initiation (initiateWithdrawal()). While the management fee is calculated and stored in the UserWithdraw.WithdrawData struct, the trading fee remains unset, causing the contract to default to using the management fee again during withdrawals.

Since the trading fee (0.035%) is significantly lower than the management fee (1%), users are charged substantially higher fees than intended. This results in financial losses for users withdrawing funds, as they pay fees at a rate nearly 30 times higher than expected.

## Recommendation
To mitigate this issue, consider applying the following changes:  
- Store the correct trading fee during withdrawal initiation by modifying initiateWithdrawal() to include the trading fee in the UserWithdraw.WithdrawData struct.  
- Use the stored trading fee instead of the management fee in the _withdraw() function when calculating sharesTradingFee.
