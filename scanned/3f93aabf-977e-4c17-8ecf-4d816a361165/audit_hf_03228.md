# [C] GLOBAL-2 | Funding Fees Not Properly Incremented

## Summary
Severity: Critical
Contest weight: 0.1820
Dataset id: 17847
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When both increasing and decreasing a position, funding fees are incremented for a user when the fees.funding.longTokenFundingFeeAmount or fees.funding.shortTokenFundingFeeAmount are greater than 0. However the funding fees are intended to be paid for by the user when they are positive and received by the user when they are negative. Currently, when funding fees are positive, the user both pays for and receives funding fees. But when they are negative, the funding fees are entirely ignored.

## Proof of Concept
https://github.com/GuardianAudits/GMX_2/blob/98d8c7dfe47f58e9c0b2efe74575795e928e5643/test/guardian/PoCs.ts#L1076

## Recommendation
Refactor the incrementClaimableFundingAmount logic when both increasing and decreasing a position so that funding fees are paid out when they are negative.
