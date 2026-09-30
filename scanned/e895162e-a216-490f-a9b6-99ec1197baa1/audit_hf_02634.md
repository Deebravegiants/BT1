# [C] Double-voting in SnapshotERC20Guild

## Summary
Severity: Critical
Contest weight: 0.3294
Dataset id: 14252
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract SnapshotERC20Guild enables users to cast votes on proposals using their voting powers. Unlike BaseERC20Guild, voting power is managed by a snapshot mechanism. One of the purposes behind most snapshot mechanisms is to prevent people flooding the voting power, after a proposal is created. In SnapshotERC20Guild, the snapshot process has unexpected behaviour:
1. lockTokens(): Calling this function does not increase proposal votingPower unless the user then calls lockTokens() again, or withdrawTokens(). This is due to calling _updateAccountSnapshot(msg.sender) on line [83], before updating the tokensLocked[msg.sender].amount on line [86].
2. withdrawTokens: Calling this function unexpectedly increases the votingPower. This is due to the function calling _updateAccountSnapshot(msg.sender) on line [100] before updating the tokensLocked[msg.sender].amount on line [102].
As a result, a malicious user is able to lock tokens, wait the allocated block.timestamp, and create a new proposal to increment the snapshotId. After this setup, they are able to call withdrawTokens(), which will withdraw the tokens from the guild contract, however the snapshot will maintain voting power as the pre-withdrawal tokensLocked[msg.sender]. After withdrawal, the malicious adversary is able to transfer the tokens to another account and repeat the process, gaining votingPower across multiple accounts that do not hold any tokens. This effectively allows a single user to double vote repeatedly on any future proposal.

## Recommendation
The testing team recommends that all tokens are appropriately locked during proposal voting and to ensure that votingPower at snapshot intervals indicate the correct amount actually held by that account. This could be achieved by placing the _updateAccountSnapshot(msg.sender) after tokensLocked[msg.sender].amount has been updated.
