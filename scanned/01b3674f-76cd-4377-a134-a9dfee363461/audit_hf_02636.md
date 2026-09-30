# [C] Incorrect votingPower Accounting

## Summary
Severity: Critical
Contest weight: 0.2239
Dataset id: 14254
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Contract SnapshotRepERC20Guild replaces token locking with a snapshot mechanism implemented in the ERC20SnapshotRep token. The guild contract derives from ERC20GuildUpgradeable or BaseERC20Guild and overrides some important functions to set votes and create proposals. The contract however, does not override the votingPower accounting algorithm, for example getTotalLocked() function. This function is used to query the total amount of tokens locked by the contract. totalLocked is then used to determine the minimum amount of tokens required to submit a proposal and to pass a proposal as defined in votingPowerForProposalCreation and votingPowerForProposalExecution respectively. As a result, anyone with an insufficient amount of tokens can propose and pass a proposal, because getVotingPowerForProposalCreation() and getVotingPowerForProposalExecution() will always produce zero.

## Recommendation
The testing team recommends refactoring the votingPower accounting and making sure that createProposal() and endProposal() satisfy the required conditions for snapshot data.
