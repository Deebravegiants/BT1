# [M] Voting Process Reverts

## Summary
Severity: Medium
Contest weight: 0.0469
Dataset id: 14263
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Because of the removal of OpenZeppelin’s ERC20VotesUpgradeable contract from the Dimo token in DimoV2.sol, it is not possible to propose a governance vote. Calls to DimoGovernance.propose() revert because propose() calls token.getPastVotes(account, blockNumber).

## Recommendation
Modify DimoV2 to reimplement OpenZeppelin’s ERC20VotesUpgradeable.
