# [M] LDTR-2 | Possible Lack Of Incentive For Liquidations

## Summary
Severity: Medium
Contest weight: 0.0652
Dataset id: 19563
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The treasuryFee is taken at a higher priority than the caller fee for liquidations. In the event where there is only enough profit to fully pay out the treasury fee, the treasury fee is paid and the callerFee is reduced. Therefore the incentive for a liquidator to expeditiously liquidate an account may be reduced and possibly insufficient in some cases.

## Recommendation
Consider taking the callerFee as the highest priority so that there is always sufficient incentive for liquidations to occur in the system.
