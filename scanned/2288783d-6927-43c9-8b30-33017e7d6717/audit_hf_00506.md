# [C] C-02 | Bond Cannot Be Returned

## Summary
Severity: Critical
Contest weight: 0.1345
Dataset id: 1964
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When submitMarketSettlementPrice is called in Vault.sol, the vault is set as the asserter in the UMA oracle. Upon successful settlement of the assertion price, the bond is returned to the vault. However, there is no mechanism to refund this bond to the user who submitted the price and paid for it. Additionally, there is no recovery function, causing the bond to remain permanently stuck in the vault.

## Recommendation
In UMASettlementModule.submitSettlementPrice, allow the caller to specify an address to be set as the asserter. Then, in Vault.submitMarketSettlementPrice, ensure the caller’s address is passed as the asserter to enable proper bond refunds.
