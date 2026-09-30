# [C] DPU-2 | Incorrect Impact Calculation

## Summary
Severity: Critical
Contest weight: 0.1731
Dataset id: 17873
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The calculation of the priceImpactAmount is computed with the params.order.sizeDeltaUsd, however the price impact that the user actually experiences is based on the adjustedSizeDeltaUsd which can be significantly smaller than the params.order.sizeDeltaUsd. This way the impact that is applied to the accounting for the pool and the impact that actually takes place can be significantly different and cause the market to start double counting funds in both the impact pool and the poolAmount.

## Proof of Concept
https://github.com/GuardianAudits/GMX_2/blob/98d8c7dfe47f58e9c0b2efe74575795e928e5643/test/guardian/PoCs.ts#L541

## Recommendation
Compute the priceImpactAmount using the adjustedSizeDeltaUsd.
