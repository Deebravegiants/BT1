# [M] Tokens not always refunded

## Summary
Severity: Medium
Contest weight: 0.0950
Dataset id: 9804
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In process.lua tokens are refunded when From ~= CollateralID. However if transfers do have From == CollateralID, the X-tag could be specified incorrectly or could not be forwarded due to a bug in the token contract. In controller.lua there is no code to refund tokens if the X-tag isn't Liquidate. This can happen with the supplied libraries, see finding Tag "X-Action" = "Liquidate" missing in Javascript library. If the tokens aren't returned then they stay stuck in process.lua / controller.lua , although they can be recovery by the protocol via batch-update and other management actions.

## Recommendation
Consider refunding tokens in more situations, for both process.lua and controller.lua.
