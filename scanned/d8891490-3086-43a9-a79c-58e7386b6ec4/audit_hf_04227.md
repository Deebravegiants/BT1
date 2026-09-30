# [M] M-21 | Lacking Incentive To Repay Debt

## Summary
Severity: Medium
Contest weight: 0.0950
Dataset id: 21121
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the BFP market users can leave accounts with realized debtUsd and enough collateral to support that debtUsd without ever repaying the debt. The debt inside these accounts will be reported in reportedDebt as profits for the LPs, however the sUSD will never be returned and never increase the creditCapacity for the market since the debt is not repaid. Over time with many positions holding unpaid debt there is an increased risk of reducing the getWithdrawableMarketUsd to a point where traders are unable to withdraw their sUSD collateral or claim their sUSD profits.

## Recommendation
Consider implementing an interest rate on unpaid debt, where traders pay a configurable rate on debt that has not yet been repaid in sUSD.
