# [M] GLOBAL-9 | Pool State Leading To Withdrawals Being Bricked

## Summary
Severity: Medium
Contest weight: 0.0811
Dataset id: 18202
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
With a range between the MAX_PNL_FACTOR_FOR_WITHDRAWALS and the MAX_PNL_FACTOR_FOR_ADL, if the profit in the pool exceeds the pnlToPoolFactor for withdrawals but is not high enough to trigger ADL, withdrawals for LPs will be bricked until users deposit more tokens into the pool and a trader decides to close their profitable position.

## Proof of Concept
https://github.com/GuardianAudits/GMX_3/blob/main/test/Guardian/PoCs/GLOBAL_9.ts

## Recommendation
Ensure that this risk is well communicated. Additionally consider setting the MAX_PNL_FACTOR_FOR_WITHDRAWALS close to the MAX_PNL_FACTOR_FOR_ADL to limit this scenario.
