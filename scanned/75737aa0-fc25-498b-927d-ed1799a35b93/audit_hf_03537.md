# [C] LCMU-1 | Any User Can Set A Token’s Decimals

## Summary
Severity: Critical
Contest weight: 0.1935
Dataset id: 19337
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There is a lack of access control on the setTokenDecimal function, therefore any user can set an arbitrary decimal amount for any tokenHash on any tokenChainId. This can easily be used to inflate how many tokens a user has on-chain and drain the vault. For example, assume WETH has 18 decimals on chain A and 18 decimals on chain B. However, Alice sets the decimals for chain A as 18 and the decimals for chain B as 19. Upon converting 1 ETH from Chain A, the amount of WETH on Chain B after conversion is tokenAmount * uint128(10 ** (dstDecimal - srcDecimal)) = 1e18 * 10**1 = 1e19. Alice was just able to turn 1 WETH on chain A into 10 WETH on chain B, and can withdraw those extra funds from the vault. The theft can be even more drastic by increasing the decimal spread between chains.

## Recommendation
Ensure only the owner can set the token decimals.
