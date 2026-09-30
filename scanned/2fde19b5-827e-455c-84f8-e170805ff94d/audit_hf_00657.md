# [M] M-05 | Strategy Deposit Might Fail Due To Limit

## Summary
Severity: Medium
Contest weight: 0.1736
Dataset id: 2193
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Asset distributions to strategies are initiated by the operators on the ledger chain. The message is then transferred to the vault chain, where the depositToStrategy function triggers asset movements from the protocolVault to the dexVault. There is a time lag between an operator initiating the process on the ledger chain and the actual execution of the transfer on the vault chain. Even if the operator initiates the process with valid distribution amounts, the Vault.depositTo function might revert with a DepositExceedLimit error due to ongoing deposits during this time lag. For example:
• dexVault deposit limit: 1000
• Current balance of the dexVault: 850
• Operator calls asset distribution with 100 on the ledger chain (valid amount at the time of initiation).
• Regular users deposit 60 more until this message reaches to vault chain.
• New balance of the dexVault: 910
• The distribution transaction fails with DepositExceedLimit.
• There is still 90 left in the deposit limit that is not filled. Since asset distributions can only be called once per period, the operator cannot attempt to distribute assets with a lower value. As a result, assets in the protocolVault remain unused.

## Recommendation
Consider implementing a separate deposit function in the dexVault for strategy deposits. This function should not revert if the full amount cannot be deposited; instead, it should deposit the available amount up to the limit.
