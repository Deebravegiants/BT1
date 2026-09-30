# [C] Snapshot Malfunction

## Summary
Severity: Critical
Contest weight: 0.2495
Dataset id: 14253
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the contract SnapshotERC20Guild, function setVote() and setSignedVote() manage the users’s votes by first checking the snapshot and then calling the parent contract’s setVote() or setSignedVote() function. The contract SnapshotERC20Guild derives from ERC20GuildUpgradeable (or BaseERC20Guild). While snapshots are used in SnapshotERC20Guild, the parent contract ERC20GuildUpgradeable does not have access to the snapshots. For example, SnapshotERC20Guild.setVote() calls the function BaseERC20Guild.setVote() which directly uses the current votingPower before processing further. The same error occurs with SnapshotERC20Guild.setVote() relying on BaseERC20Guild.setSignedVote(). These checks against the parent contract’s votingPower do not take into account applied snapshots in the child contract. If the voters withdraw their tokens after proposal creation and before voting, the parent contract will revert with Invalid votingPower message.

## Recommendation
The testing team recommends refactoring the votingPower checks across parent and child contracts to allow votingPower checks to be performed only on child contracts. This will preserve votingPower data across different implementations, for example, through snapshots. Alternatively, the voting logic could be moved to the child contract to avoid calling the parent contract’s functions.
