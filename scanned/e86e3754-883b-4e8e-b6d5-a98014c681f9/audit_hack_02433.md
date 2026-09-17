# [M] Unprotected Initialization Function

## Summary
Severity: Medium
Source: https://github.com/matter-labs/system-contracts/blob/4ad1f26ae205d5a973216d141833e0ac37d72ec8/contracts/L2EthToken.sol#L35
Type: audit-issue

## Details
In the `L2EthToken` contract, an [unresolved comment](https://github.com/matter-labs/system-contracts/blob/4ad1f26ae205d5a973216d141833e0ac37d72ec8/contracts/L2EthToken.sol#L35) acknowledges the fact that the `initialization` function is unprotected and anyone could set the `l2Bridge` address if they call the function before the legitimate operator. The comment describes the problem without presenting a solution.

Consider using the TypeScript-based templating system that is already present in the codebase to inject a constant address that limits the `initialization` call to one specific `msg.sender`.

_**Update:** Acknowledged, not resolved. The Matter Labs team stated:_

> _We plan to rethink the approach of bridging ether in the new upgrade, the issue will be resolved there._
