# [M] ISU-5 | Incorrect Withdrawal Maturity Check

## Summary
Severity: Medium
Contest weight: 0.1346
Dataset id: 20585
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Issuance checks whether a withdrawal has matured in order to allow calling completeWithdrawEarly only on non-matured withdrawals. EigenLayer makes withdrawal requests wait roughly a week after they got queued in order to be able to react and punish in cases where the staker/operator of the staker acted maliciously in any sort of way. On the contrary the logic that enforces this in the Issuance contract implements the following access control: block.number > withdraw.startBlock + vault.delegationManager().withdrawalDelayBlocks() It explicitly requires that the current block is greater than the queue start plus the delay period, thus allowing early withdrawals even when the EigenLayer withdrawal has already matured. This allows matured loans to be "bought out” in a block they are already completable in, thus introducing unexpected behavior and possible loss of funds for the oldOwner through MEV.

## Recommendation
block.number >= withdraw.startBlock + vault.delegationManager().withdrawalDelayBlocks()
