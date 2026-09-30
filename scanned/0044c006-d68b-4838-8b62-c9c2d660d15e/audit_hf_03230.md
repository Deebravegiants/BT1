# [C] IOU-1 | Token Transferred To Wrong Market

## Summary
Severity: Critical
Contest weight: 0.1862
Dataset id: 17849
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When creating an increase order, the collateral token gets sent to the market parameter on the order. This becomes problematic when a swapPath is provided, and the initialCollateralToken is not a token found in the order’s market. Consider the following example: 1) Order with ETHUSD market, WBTC as initial collateral, and [BTCUSD, ETHUSD] swapPath. 2) WBTC gets transferred to the ETHUSD market rather than the BTCUSD market 3) BTCUSD market accounting is now off as the pool thinks there is more WBTC backing positions than there really is.

## Proof of Concept
https://github.com/GuardianAudits/GMX_2/blob/98d8c7dfe47f58e9c0b2efe74575795e928e5643/test/guardian/PoCs.ts#L1331

## Recommendation
Transfer the collateral token to the first market in the swapPath if a swapPath is provided.
