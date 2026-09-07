# [?] improve: [L06] Add reentrancy guards to all public methods (#92)

## Summary
Severity: Unknown
Chain: Across
Component: across-protocol/contracts
Published: 2022-03-17
Source: https://github.com/across-protocol/contracts/commit/21185d35f97708e8212bf4435dec0fb3952ab796
Type: security-commit

## Details
improve: [L06] Add reentrancy guards to all public methods (#92)

* improve: Add reentrancy guards to all public methods

* Add reentrancy guard to onlyAdmin override

* Add comments

* merge

* remove nonReentrant from _requireAdminSender

* Update Arbitrum_SpokePool.sol

* add reentrancy guard to spoke pool

* Update HubPool.sol

* Add tests
