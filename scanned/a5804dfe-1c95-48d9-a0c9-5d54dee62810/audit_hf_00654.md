# [M] M-02 | Missing Payable Modiﬁer Function

## Summary
Severity: Medium
Contest weight: 0.1130
Dataset id: 2190
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the depositToStrategy function, the contract attempts to call IDexVault(dexVault).depositTo{value: fee}(...) but the function itself is not declared as payable. As a result, it cannot receive native assets in the current transaction, causing a revert if no native assets are already in the contract’s balance. This breaks the expected flow of paying a fee at runtime, preventing the contract from funding the DexVault deposit call. Furthermore, in the VaultCrossChainManager contract’s _lzReceive function, the ASSETS_DISTRIBUTION case calls IProtocolVault(vault).depositToStrategy(...) but does not supply msg.value for the fee.

## Recommendation
Add the payable modifier to depositToStrategy so that it can accept native assets in the same transaction. At the same time, ensure that the cross-chain message in VaultCrossChainManager includes the fee in msg.value when relaying ASSETS_DISTRIBUTION, so the contract handles and transfers the deposit fee to the DexVault.
