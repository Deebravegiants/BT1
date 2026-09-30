# [H] H-06 | Withdraw Message Sent Even If _validReceiver Check Fails

## Summary
Severity: High
Contest weight: 0.2300
Dataset id: 2217
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Vault.withdraw function IVaultCrossChainManager(crossChainManagerAddress).withdraw(vaultWithdrawData) is called before verifying that the receiver is valid. Consequently, if _validReceiver(data.receiver, address(tokenAddress)) returns false, the vault still sends a cross‐chain message to the ledger acknowledging a “successful” withdrawal. Meanwhile, the local code emits only a WithdrawFailed event and never transfers the tokens to the ProtocolVault. This leaves the ledger believing the user’s withdrawal went through, while in reality no tokens were actually delivered. As a result, the user’s ledger state and on-chain vault state become out of sync. The ledger sees a final “withdraw finish,” but the vault never transferred tokens if the receiver check fails. This scenario could strand the user’s funds or require an off-chain correction.

## Recommendation
If the vault does not transfer tokens because _validReceiver(data.receiver, address(tokenAddress)) returned false, consider sending a “withdraw failure” message back to the ledger or omit sending a “successful” cross‐chain call. This ensures the ledger and vault remain consistent, reflecting that the withdrawal did not finalize.
