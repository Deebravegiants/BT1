# [M] MKTU-4 | Users Paid Funding Fees When They Should Pay

## Summary
Severity: Medium
Contest weight: 0.0956
Dataset id: 19230
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
It is possible for shorts to get paid when longs should pay shorts (long OI > short OI) and vice versa. This is because it may take a certain duration until the savedFundingFactorPerSecond flips payment sides and accurately represents payment direction. Ultimately this functionality misaligns incentives during this period, where traders who imbalance the pool aren’t discouraged by funding fee payments.

## Proof of Concept
https://github.com/GuardianAudits/GMX-Updates-9-4-23/blob/25b1d86cbd3a807db6c7b03b3d0fe9d5b27ae924/test/guardian/PoCs.ts#L448

## Recommendation
Consider resetting the fundingFactorPerSecond entirely when the OI imbalance direction changes.
