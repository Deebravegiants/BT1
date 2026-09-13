# [C] [](https://github.com/alexbehrens/optimismc03-unbounded-nuisance-gas)\[C03\] Unbounded nuisance gas

## Summary
Severity: Critical
Source: https://github.com/ben-chain/contracts-v2/blob/a935e276f5620b40802b52721e3474232e458f72/contracts/optimistic-ethereum/OVM/execution/OVM%5FExecutionManager.sol#L1836
Type: audit-issue

## Details
When a transaction is executed, its nuisance gas budget [is limited](https://github.com/ben-chain/contracts-v2/blob/a935e276f5620b40802b52721e3474232e458f72/contracts/optimistic-ethereum/OVM/execution/OVM%5FExecutionManager.sol#L1836) to the transaction gas limit. Additionally, the nuisance gas is [limited in every call frame](https://github.com/ben-chain/contracts-v2/blob/a935e276f5620b40802b52721e3474232e458f72/contracts/optimistic-ethereum/OVM/execution/OVM%5FExecutionManager.sol#L963) to the gas provided for that call. However, it is not limited by the [available nuisance gas before the call](https://github.com/ben-chain/contracts-v2/blob/a935e276f5620b40802b52721e3474232e458f72/contracts/optimistic-ethereum/OVM/execution/OVM%5FExecutionManager.sol#L962).

As a result, if the remaining nuisance gas budget is below the remaining transaction gas before an external call, the nuisance gas budget for the call frame will be incorrectly increased, and the call will be able to consume more nuisance gas than it should be allowed. In this scenario, the overall nuisance budget calculation performed after the call [will negative overflow](https://github.com/ben-chain/contracts-v2/blob/a935e276f5620b40802b52721e3474232e458f72/contracts/optimistic-ethereum/OVM/execution/OVM%5FExecutionManager.sol#L1047). In practice, this means there is no limit to the amount of nuisance gas that can be used in a transaction, as long as each call frame restricts its nuisance gas usage to its own regular gas limit.

Consider ensuring the nuisance gas budget of each call frame cannot exceed the overall budget.

_**Update**: Fixed in [pull request #1366](https://github.com/ethereum-optimism/optimism/pull/1366/commits/a2346c291797813f99b32e1d92f26c33a6d55d2d)._
