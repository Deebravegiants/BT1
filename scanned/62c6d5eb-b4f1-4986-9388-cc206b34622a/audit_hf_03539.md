# [H] LGR-2 | Rounded Frozen Balance Bricks Withdrawals

## Summary
Severity: High
Contest weight: 0.3464
Dataset id: 19339
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When making a withdrawal, the action goes from the ledger chain to the vault chain back to the ledger chain. When sending the message to the vault, withdraw is called which converts the fee to the proper amount of decimals on the vault chain using convertDecimal. However, truncation may occur due to the collateral on the vault chain having fewer decimals than on the ledger chain. For example, let's assume the fee is initially 1 wei and the decimal spread between chains is 12. When executeWithdrawAction is triggered on the ledger, 1 wei of fees have been accounted for such that the VaultManager freezes 1 less wei than the withdraw.tokenAmount transmitted: vaultManager.frozenBalance(tokenHash, withdraw.chainId, withdraw.tokenAmount - withdraw.fee). Once ILedgerCrossChainManager(crossChainManagerAddress).withdraw(withdraw) is called, decimal conversion occurs and the new fee to be sent to the vault chain is 1 / 10**12 = 0. When the message finally arrives back to the ledger to finish withdrawal vaultManager.finishFrozenBalance(withdraw.tokenHash, withdraw.chainId, withdraw.tokenAmount - withdraw.fee) is called. Because the withdraw.fee is smaller than accounted for initially (1 wei vs 0 wei), more is unfrozen than was originally frozen upon executeWithdrawAction, which will cause an arithmetic underflow in the VaultManager and brick all withdrawals until a user deposits to cover the deficit. This can continuously be done maliciously to continuously block withdrawals from occurring.

## Proof of Concept
https://github.com/GuardianAudits/OrderlyEVMContractsSuite/blob/4e216c2befe63c5379059f9359a7b3a0da008a71/test/GuardianPOC.t.sol#L158

## Recommendation
Round beforehand such that the rounded value when finishing the withdrawal is the same as when starting the withdrawal. Alternatively, use higher precision for token amounts although this may be a considerable refactor.
