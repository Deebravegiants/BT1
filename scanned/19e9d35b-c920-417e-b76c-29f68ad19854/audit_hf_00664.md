# [C] C-07 | Compilation Error Due To Naming Mismatch

## Summary
Severity: Critical
Contest weight: 0.1029
Dataset id: 2200
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
EventTypes.Withdraw2Contract struct in the orderly-contract-evm repo has a uint256 clientId parameter, which is used instead of periodId. However, the orderly-evm-cross-chain repo attempts to read periodId from this struct in the VaultCrossChainManagerUpgradeable.receiveMessage function, causing a TypeError compilation error.

## Recommendation
Update the orderly-evm-cross-chain repo to reflect the changes in the orderly-contract-evm repo.
