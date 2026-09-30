# [C] DIEM-3 | Liquidation will fail due to insufficient funds

## Summary
Severity: Critical
Contest weight: 0.1696
Dataset id: 118
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the liquidate function when a position is insolvently liquidated the PnL amount transferred to the IVXLP contract is determined to be the total balance of the portfolio in a dollar amount. If a token in the portfolio is not USDC, it will be swapped for USDC and incur a fee as well as slippage before the USDC amount is received in the Diem contract. Because the Diem contract receives less USDC, it will not have sufficient funds to transfer to all necessary stakeholders. The lack of funds will lead to the transaction reverting, making it impossible to liquidate a position that requires a swap.

## Recommendation
Use the amount received after liquidate() to perform the liquidation during insolvent closes. This will ensure that there are enough funds to finish execution.
