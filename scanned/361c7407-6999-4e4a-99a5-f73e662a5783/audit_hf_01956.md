# [M] NFTR-1 | Centralization Risk

## Summary
Severity: Medium
Contest weight: 0.1080
Dataset id: 10821
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The owner address has the ability to repeatedly change namingPriceRNM by calling updateNamingPriceRNM, but the function lacks any lower and upper bounds on the input. As a result, the owner can modify the RNM price to be as large as possible and frontrun a buyer’s transaction. This would lead to the user experiencing a larger decrease of assets than intended. Additionally, the owner address holds potentially exploitative abilities to: withdraw, withdrawRNM, curateCollection, updateNamingCreditsProtocolFeeRecipient, shutOffAssignments, assignNamingCredits, setSpecialNames, updateNamingPriceEther, updateProtocolFeeRecipient, updateRnmNamingStartBlock.

## Recommendation
Consider defining lower and upper bounds on namingPriceRNM. Furthermore, consider making owner a multi-sig, optionally with a timelock for improved community oversight.
