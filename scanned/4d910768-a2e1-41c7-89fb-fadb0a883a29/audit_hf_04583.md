# [M] M-16 | addLiquidity Fails For Fee-On-Transfer Tokens

## Summary
Severity: Medium
Contest weight: 0.0629
Dataset id: 22186
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When addLiquidityV2 is called, an amount of _pairedLPToken is transferred into the contract, and the same amount is used to add liquidity in the DEX_HANDLER. However, if the pairedLPToken is a Fee-on-Transfer token, then the amount received would be less than expected due to a fee. Therefore, the DEX_HANDLER.addLiquidity call could fail due to insufficient tokens.

## Recommendation
Use actual balance of pairedLPTokens when calling DEX_HANDLER.addLiquidity.
