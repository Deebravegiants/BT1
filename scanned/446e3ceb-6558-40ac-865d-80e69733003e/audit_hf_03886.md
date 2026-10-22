# [H] Wrong accounting of the storage balances re-

## Summary
Severity: High
Contest weight: 0.2899
Dataset id: 20169
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Wrong accounting of the storage balances results for the protocol to be in debt even when the bad debt is repaid.
When a position is fully closed, it can result in accruing bad debt or being in profit and repaying the borrowed liquidity which all depends on the amount_out_received from the swap.
In a bad debt scenario the function calculates the bad debt and accrues it based on the difference between the position debt and the amount out received from the swap. And after that repays the liquidity providers with the same received amount from the swap.
The mapping total_debt_amount holds all debt borrowed from users, and this amount accrues interest with the time.
Prior to closing a position, the bad debt is calculated and accrued to the mapping bad_debt, but it isn't subtracted from the mapping total_debt_amount which holds all the debt even the bad one accrued through the time.
As the bad debt isn't subtracted from the total_debt_amount when closing a position, even after repaying the bad debt, it will still be in the total_debt_amount, which will prevent the full withdrawing of the liquidity funds.
The issue leads to liquidity providers unable to withdraw their full amount of funds, as even after repaying the bad debt it will still be in the total_debt_amount mapping.

## Recommendation
The only way to fix this problem is to repay the position debt amount prior to closing a position and not only the received amount from the swap. Because total_debt_amount holds the bad debt as well.
