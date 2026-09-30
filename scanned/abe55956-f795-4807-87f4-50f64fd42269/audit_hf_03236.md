# [H] DOU-3 | Incorrect LimitDecrease Size Assignment

## Summary
Severity: High
Contest weight: 0.1412
Dataset id: 17855
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When the sizeDeltaUsd of a LimitDecrease order exceeds the position sizeInUsd, the order lives on in the orderStore but the sizeDeltaUsd of the order is set to the result.adjustedSizeDeltaUsd, which is the amount that the order was just able to decrease the position by, not the amount that the order has left to decrease.

## Proof of Concept
https://github.com/GuardianAudits/GMX_2/blob/98d8c7dfe47f58e9c0b2efe74575795e928e5643/test/guardian/PoCs.ts#L1976

## Recommendation
Assign the sizeDeltaUsd of the order to be the order.sizeDeltaUsd() - result.adjustedSizeDeltaUsd.
