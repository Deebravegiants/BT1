# [M] M-15 | Fee Change Hurts Traders

## Summary
Severity: Medium
Contest weight: 0.0671
Dataset id: 151
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the _prepareValidateOpenPositionData function the startPrice is affected by the current fee in storage, however this fee may be different than the one that was applied upon initiation and validated against the userMaxPrice.
This is in contrast to the deposit and withdrawal flow, where the vaultFeeBps are cached onto the deposit/withdrawal object and used during validation.

## Recommendation
Consider caching the _positionFeeBps value upon initiation in the open position object to be applied on validation.
