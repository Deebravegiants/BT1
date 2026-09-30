# [M] M-19 | Debt Is Not Reflected In CreditCapacity Until Repaid

## Summary
Severity: Medium
Contest weight: 0.1618
Dataset id: 2284
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the payDebt function users may pay their existing debt with sUSD from outside of the BFP market system. This sUSD is deposited for the market with the depositMarketUsd function on the Synthetix V3 core system.
The depositMarketUsd function will increase the creditCapacity of the market by the repaid amount.
This net increase in the market’s creditCapacity counts towards the minimumCredit validation for the market, however it is not added until the trader repays their debt.
Regardless of when the trader pays their debt the LPs receive the value lost by the trader as a delta reduction in their debt. This debt reduction may not be fully utilizable by the LPs until the trader’s debt is repaid as the minimumCredit validation would fail because the debt has not been added to the market’s creditCapacity.
Trader’s can therefore unjustly lock a portion of the LPs rightful gains until their debt is repaid.
Notice that this will only occur when a market’s creditCapacity is close to the minimumCredit and will not always have a noticeable locking effect on the LPs gains.

## Recommendation
Consider offsetting this creditCapacity payDebt time mismatch by reducing the minimumCredit by the amount of outstanding debt that has yet to be paid. This way the LPs can mint using their realized debt reduction before trader’s repay their debt.
