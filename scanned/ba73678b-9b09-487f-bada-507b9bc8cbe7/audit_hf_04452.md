# [H] H-03 | Long Funding Is Never Claimed

## Summary
Severity: High
Contest weight: 0.1316
Dataset id: 21943
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When the afterOrderExecution function is called, Gamma has the opportunity to collect funding fees
for both the long and short tokens.
It is important for Gamma to claim these fees, otherwise they will remain in GXM. However, only the
short funding fee is currently being claimed (tokens[0] = order.addresses.initialCollateralToken).
This issue means that some funding fees will go unclaimed, resulting in the expected yield not being
distributed to users as intended.

## Recommendation
Consider claiming both long and short funding fees.
