# [H] GLPM-2 | USDC vs USDC.e

## Summary
Severity: High
Contest weight: 0.1620
Dataset id: 19345
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Currently GLP consists of a large amount of USDC.e (bridged USDC), which has a different token address than USDC. On the other hand, GMX V2 pools all use USDC. Because a user is required to pass a migrationItem.short.token that matches the cache.market.shortToken, they cannot redeem with USDC.e as tokenOut since the short token validation will revert. Rather, the user is forced to redeem for the limited amount of USDC directly so that they can deposit the USDC into the GMX V2 market.

## Recommendation
In the case of USDC, modify the InvalidShortTokenForMigration check such that USDC.e can still pass and then be swapped for native USDC. Furthermore, consider adding a state check after the external calls to check the token balances of the depositVault, to ensure the user has not mistakenly sent the USDC.e to the GMX V2 system and lost it.
