# [H] H-15 | Lenders can deposit into full SuperPools

## Summary
Severity: High
Contest weight: 0.2040
Dataset id: 2530
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The _supplyToPools function loops through all BasePools in the queue and supplies funds to them as long as the cap is not reached. But this function does not revert if all caps were reached and it was impossible to supply funds to any pool. Therefore lenders are still able to deposit funds into a full SuperPool and mint shares which is very capital inefficient and will reduce the yield per share of all lenders.
Example:
• X lenders deposit a sum of Y USDC into pools with 5% APY over the SuperPool and reach the cap
• These lenders now receive 5% APY on their deposits
• More lenders deposit into the SuperPool which is already full
• The new lender's funds are not put to work but they still receive shares of the SuperPool and therefore a share of the yield from the BasePools
• Every lender now receives less than 5% APY on their deposits

## Recommendation
Revert at the end of the _supplyToPools function.
