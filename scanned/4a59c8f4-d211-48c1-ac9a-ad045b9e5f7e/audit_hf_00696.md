# [C] C-01 | Proﬁtable Self Liquidations

## Summary
Severity: Critical
Contest weight: 0.2116
Dataset id: 2247
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a user deposits, there is no validation that the amount that they deposit is enough to cover the fee for liquidateMarginOnly(). This allows a user to deposit 1 wei, and liquidate themselves immediately to realize a proﬁt. Below are the calculations based off current ETH prices:
Cost of Deposit: 0.001633216 ETH
Cost of Liquidation: 0.001899712 ETH
Collateral Cost: 0.000000000000000001 ETH
Total Cost ETH: 0.003656128000000001 ETH
Total Cost USD: $12.4097 = 0.003656128000000001 ETH * $3,394.23
Reward sUSD: 24.0608
Proﬁt: $11.6511

## Proof of Concept
https://github.com/GuardianAudits/snx-bfp-1/blob/POC_BFP/markets/bfp-market/test/integration/modules/guardian/pocs/profitableSelfLiquidation.test.ts

## Recommendation
Verify that if the user is depositing, the collateral amount must be equal or greater than the highest possible marginLiquidationOnly reward. Additionally, validate that the amount of collateral left after withdrawing is suﬃcient to cover the highest possible marginLiquidationOnly reward if it is nonzero.
