# [M] \[M01\] Complicated state updates

## Summary
Severity: Medium
Source: https://github.com/AudiusProject/audius-protocol/blob/6f3b31562b9d4c43cef91af0a011986a2580fba2/eth-contracts/contracts/DelegateManager.sol#L116
Type: audit-issue

## Details
When stake balances are modified (through [delegateStake](https://github.com/AudiusProject/audius-protocol/blob/6f3b31562b9d4c43cef91af0a011986a2580fba2/eth-contracts/contracts/DelegateManager.sol#L116), [requestUndelegateStake](https://github.com/AudiusProject/audius-protocol/blob/6f3b31562b9d4c43cef91af0a011986a2580fba2/eth-contracts/contracts/DelegateManager.sol#L183), [cancelUndelegateStake](https://github.com/AudiusProject/audius-protocol/blob/6f3b31562b9d4c43cef91af0a011986a2580fba2/eth-contracts/contracts/DelegateManager.sol#L222), [undelegateStake](https://github.com/AudiusProject/audius-protocol/blob/6f3b31562b9d4c43cef91af0a011986a2580fba2/eth-contracts/contracts/DelegateManager.sol#L239), and [slash](https://github.com/AudiusProject/audius-protocol/blob/6f3b31562b9d4c43cef91af0a011986a2580fba2/eth-contracts/contracts/DelegateManager.sol#L432)), multiple operations are executed to increase or decrease the values of the state variables related to the updated stake status. This is error prone, as shown by the critical issue _“A malicious delegator can permanently lock all stake and rewards for a victim service provider and all of its honest delegators”_ where one of the values was not correctly updated.

A similar pattern is implemented to track the number of votes for [Governance](https://github.com/AudiusProject/audius-protocol/blob/6f3b31562b9d4c43cef91af0a011986a2580fba2/eth-contracts/contracts/Governance.sol) proposals.

Consider encapsulating these operations into separate functions, one for each type of state update. This way it will be clearer to review that the operations are complete, consistent, and complementary. Some duplication can be removed, and these functions can be thoroughly tested in isolation.

Consider [formal verification](https://en.wikipedia.org/wiki/Formal%5Fverification) to prove that these critical state variables will always behave as expected and keep the system in a consistent state.

_**Update:** Fixed in [pull request #539](https://github.com/AudiusProject/audius-protocol/pull/539). Most of the logic was encapsulated in new internal functions, such as the [\_updateDelegatorStake](https://github.com/AudiusProject/audius-protocol/blob/e16dd3e8af4587bacad902bb66a718b60658b972/eth-contracts/contracts/DelegateManager.sol#L150) and the [\_updateServiceProviderLockupAmount](https://github.com/AudiusProject/audius-protocol/blob/e16dd3e8af4587bacad902bb66a718b60658b972/eth-contracts/contracts/DelegateManager.sol#L813) functions of the `DelegateManager` contract, and the [\_decreaseVoteMagnitudeNo](https://github.com/AudiusProject/audius-protocol/blob/e16dd3e8af4587bacad902bb66a718b60658b972/eth-contracts/contracts/Governance.sol#L689) and the [\_increaseVoteMagnitudeYes](https://github.com/AudiusProject/audius-protocol/blob/e16dd3e8af4587bacad902bb66a718b60658b972/eth-contracts/contracts/Governance.sol#L671) functions of the `Governance` contract._
