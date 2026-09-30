# [C] DPU-4 | Wrong Token Amount Applied

## Summary
Severity: Critical
Contest weight: 0.1394
Dataset id: 17875
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The pnlAmountForPool is either the collateralToken if the user realized losses or the pnlToken if the user realized gains. However the applyDeltaToPoolAmount treats this amount as collateralToken no matter what, therefore perturbing the accounting of the pool by applying a pnlToken amount to a collateralToken amount.

## Proof of Concept
https://github.com/GuardianAudits/GMX_2/blob/98d8c7dfe47f58e9c0b2efe74575795e928e5643/test/guardian/PoCs.ts#L756

## Recommendation
Be sure to applyDeltaToPoolAmount for the correct token that is being removed from the pool.
