# [C] DPCU-1 | Position fundingFeeAmountPerSize Errantly Reset

## Summary
Severity: Critical
Contest weight: 0.1786
Dataset id: 18871
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When the fees.totalCostAmountExcludingFunding is paid with any amount of secondary tokens the fees object is replaced with an empty instance. In this case however there can be a position that remains, and it will be stamped with a fundingFeePerSize value of 0 from this empty fees instance. Therefore the position must now pay all funding fees since the inception of the market. In all likelihood the position will then be immediately liquidated leading to an immediate significant loss of assets for the position that would have remained.

## Proof of Concept
https://github.com/GuardianAudits/GMX-6/blob/main/test/guardian/DPCU-1.ts

## Recommendation
Do not reset the fees.funding.funding.latestFundingFeeAmountPerSize on the fees object when the position can remain, e.g. outside of any insolvent close.
