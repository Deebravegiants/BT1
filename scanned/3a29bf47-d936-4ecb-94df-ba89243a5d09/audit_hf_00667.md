# [M] M-14 | Vault LZ Fee Can Be Lost

## Summary
Severity: Medium
Contest weight: 0.0876
Dataset id: 2203
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When ProtocolVault.depositToStrategy() is called, the dexVault.getDepositFee() will be forwarded to dexVault. depositTo(). The vault will then use that value to pay for LZ fees. However, the vault has a depositFeeEnabled boolean. It will use the msg.value send to depositTo() to pay for the fees only if this flag is set to true. Otherwise, the sent native token will not be used and remain stuck in the contract.

## Recommendation
Forward the fee from ProtocolVault to Vault only if depositFeeEnabled = true. IMPORTANT: If you implement this fix, any value provided by the executor to pay the fees will now be stuck in ProtocolVault. You should come up with a solution for these funds. You can: transfer the fee to the vault if depositFeeEnabled = true otherwise transfer it to the VaultCrossChainManagerUpgradeable
