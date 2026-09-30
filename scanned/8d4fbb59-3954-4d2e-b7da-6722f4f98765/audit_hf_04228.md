# [M] M-06 | Merging Accounts May Fail For Multicollateral Positions

## Summary
Severity: Medium
Contest weight: 0.1343
Dataset id: 21124
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When merging accounts, the function executes getMatchingMarketCollateral which returns the matching margin collateral equal to market. This function will return a matching synthMarketId and fromAccountCollateral. If the fromId account has multiple collaterals, the getMatchingMarketCollateral function will only return the last collateral that matched. This means that the merge will transfer one collateral to the toId account, and leave the other 2 in the fromId account. The issue is that the merge will then transfer a portion of the collateral but the whole position size. If the last collateral that matched is the smallest one in terms of USD, then the toPosition might invalidate the Initial Margin check and revert.

## Proof of Concept
https://github.com/GuardianAudits/synthetix-pocs/blob/main/markets/bfp-market/test/integration/modules/team2PoCs.test.ts#L108

## Recommendation
Transfer all collaterals with available balance to the toId account.
