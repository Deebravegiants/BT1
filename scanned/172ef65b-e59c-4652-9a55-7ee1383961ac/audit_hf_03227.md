# [C] DOU-1 | Swap From Arbitrary Market

## Summary
Severity: Critical
Contest weight: 0.1703
Dataset id: 17846
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When swapping after decreasing an order, the first market in the swapPath is not required to be the market the position was in. This way a user can specify a market that accepts the result.outputToken and the result.outputAmount will be swapped from that market, but the user’s profits are left in the original market. This breaks the accounting system in the market that was provided in place of the position’s market as the first market in the swapPath.

## Proof of Concept
https://github.com/GuardianAudits/GMX_2/blob/98d8c7dfe47f58e9c0b2efe74575795e928e5643/test/guardian/PoCs.ts#L969

## Recommendation
Transfer the funds to the first market in the swapPath, or require that the first market be the position’s market.
