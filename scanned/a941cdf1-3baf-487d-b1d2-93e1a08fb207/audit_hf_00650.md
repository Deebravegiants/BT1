# [C] C-03 | handleOpFromVault Function Does Not Scale Decimals

## Summary
Severity: Critical
Contest weight: 0.1962
Dataset id: 2178
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the handleOpFromVault function, the ProtocolVaultLedger contract treats operationData.amount as a direct integer without adjusting for the underlying token’s decimals. Assets and shares are supposed to be stored with 6 decimals precision. As per the code comments, this accountToken will be USDC and USDC has 6 decimals in most of the chains. However USDC has 18 decimals instead of 6 on the following chains:
• Oasys
• BNB
• OKX Chain
• Sora
• Kucoin Chain
• Telos
• Conflux
• Bitgert
If accountToken has a different number of decimals than 6 the ProtocolVaultLedger contract calculations end up over-counting or under-counting actual token amounts which would totally break the accounting in the contract.

## Recommendation
Normalize operationData.amount according to the token’s decimals before updating ProtocolVaultLedger’s state. A robust approach is to store each token’s decimal information on-chain and adjust incoming amounts consistently.
