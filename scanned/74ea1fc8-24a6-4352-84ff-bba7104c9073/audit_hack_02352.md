# [M] \[M02\] Inconsistently checking initialization

## Summary
Severity: Medium
Source: https://github.com/AudiusProject/audius-protocol/blob/6f3b31562b9d4c43cef91af0a011986a2580fba2/eth-contracts/contracts/InitializableV2.sol#L19
Type: audit-issue

## Details
When a contract is initialized, its [isInitialized state variable is set to true](https://github.com/AudiusProject/audius-protocol/blob/6f3b31562b9d4c43cef91af0a011986a2580fba2/eth-contracts/contracts/InitializableV2.sol#L19). Since interacting with uninitialized contracts would cause problems, the [\_requireIsInitialized](https://github.com/AudiusProject/audius-protocol/blob/6f3b31562b9d4c43cef91af0a011986a2580fba2/eth-contracts/contracts/InitializableV2.sol#L22) function is available to make this check.

However, this check is not used consistently. For example, it is used in the [getVotingQuorum function](https://github.com/AudiusProject/audius-protocol/blob/6f3b31562b9d4c43cef91af0a011986a2580fba2/eth-contracts/contracts/Governance.sol#L636) of the `Governance` contract, but it is not used in the [getRegistryAddress](https://github.com/AudiusProject/audius-protocol/blob/6f3b31562b9d4c43cef91af0a011986a2580fba2/eth-contracts/contracts/Governance.sol#L642) function of the same contract. There is no obvious difference between the functions to explain this difference, and it could be misleading and cause uninitialized contracts to be called.

Consider calling `_requireIsInitialized` consistently in all the functions of the `InitializableV2` contracts. If there is a reason to not call it in some functions, consider documenting it. Alternatively, consider removing this check altogether and preparing a good deployment script that will ensure that all contracts are initialized in the same transaction that they are deployed. In this alternative, it would be required to check that contracts resulting from new proposals are also initialized before they are put in production.

_**Update:** Fixed in pull requests [#587](https://github.com/AudiusProject/audius-protocol/pull/587) and [#594](https://github.com/AudiusProject/audius-protocol/pull/594). The `requireIsInitialized` check has been added to all the externally accessed functions of contracts that inherit from `InitializableV2`._
