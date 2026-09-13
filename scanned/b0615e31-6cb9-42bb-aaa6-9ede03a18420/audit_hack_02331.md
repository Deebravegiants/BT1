# [M] \[M01\] Lack of input validation

## Summary
Severity: Medium
Source: https://github.com/compound-finance/compound-protocol/blob/f86c247f6f81e14f8e0fd78402653a0b8371266a/contracts/Governance/GovernorBravoDelegator.sol#L7
Type: audit-issue

## Details
The [constructor](https://github.com/compound-finance/compound-protocol/blob/f86c247f6f81e14f8e0fd78402653a0b8371266a/contracts/Governance/GovernorBravoDelegator.sol#L7) in `GovernanceBravoDelegator` lacks input validation on all passed-in parameters, allowing things like [admin to be set to address(0)](https://github.com/compound-finance/compound-protocol/blob/f86c247f6f81e14f8e0fd78402653a0b8371266a/contracts/Governance/GovernorBravoDelegator.sol#L28), the addresses of `comp` or `timelock` to be [incorrectly set](https://github.com/compound-finance/compound-protocol/blob/f86c247f6f81e14f8e0fd78402653a0b8371266a/contracts/Governance/GovernorBravoDelegate.sol#L28-L29), or [proposalThreshold to be set arbitrarily](https://github.com/compound-finance/compound-protocol/blob/f86c247f6f81e14f8e0fd78402653a0b8371266a/contracts/Governance/GovernorBravoDelegate.sol#L32) despite [the MIN\_PROPOSAL\_THRESHOLD](https://github.com/compound-finance/compound-protocol/blob/f86c247f6f81e14f8e0fd78402653a0b8371266a/contracts/Governance/GovernorBravoDelegate.sol#L243). Additionally, functions such as [\_setImplementation](https://github.com/compound-finance/compound-protocol/blob/f86c247f6f81e14f8e0fd78402653a0b8371266a/contracts/Governance/GovernorBravoDelegator.sol#L36), [\_setVotingDelay](https://github.com/compound-finance/compound-protocol/blob/f86c247f6f81e14f8e0fd78402653a0b8371266a/contracts/Governance/GovernorBravoDelegate.sol#L216) and [\_setVotingPeriod](https://github.com/compound-finance/compound-protocol/blob/f86c247f6f81e14f8e0fd78402653a0b8371266a/contracts/Governance/GovernorBravoDelegate.sol#L228) contain no input checks and allow sensitive values to be set to any arbitrary value.

Consider bounding inputs to reasonable ranges and excluding certain values, such as `address(0)` or `uint256(0)` from being successfully passed in. This will reduce the surface for error when using these functions.

_**Update**: Partially fixed in [pull request #5](https://github.com/Arr00-Blurr/compound-protocol/pull/5). There are still no input checks on the [\_setImplementation](https://github.com/Arr00-Blurr/compound-protocol/blob/b49b3192fe6a92eb1e9e0619481c03aa1c2c13aa/contracts/Governance/GovernorBravoDelegator.sol#L36) function._
