# [C] SWPU-1 | Price Impact Not Transferred

## Summary
Severity: Critical
Contest weight: 0.1842
Dataset id: 17845
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When swapping, the current MarketToken transfers the poolAmountOut to the next pool in the swap route, but this value does not include any positive price impact that the user might have accrued. This way the positive impact amount is left, unaccounted for, in the current MarketToken contract and the following MarketToken in the route “thinks” it has received the positive impact amount but it hasn’t. This causes a deficit in the accounting for the MarketToken which was told that it received the positive impact amount, but never did.

## Proof of Concept
https://github.com/GuardianAudits/GMX_2/blob/98d8c7dfe47f58e9c0b2efe74575795e928e5643/test/guardian/PoCs.ts#L897

## Recommendation
Be sure to send the positive impact amount to the next MarketToken in the swap route.
