# [M] [Tomo-M1] Solidity version 0.8.13 has vulnerability

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-frankendao
Published: 2022-11-16
Source: https://github.com/sherlock-audit/2022-11-frankendao-judging/issues/62
Type: sherlock-finding

## Details
Tomo

medium

# [Tomo-M1] Solidity version 0.8.13 has vulnerability

## Summary

**Solidity version 0.8.13 has a vulnerability**

## Vulnerability Detail

The solidity version 0.8.13 has a vulnerability and some contracts applicable for this issue.

**Vulnerability related to ABI-encoding**

> You might be affected if you pass a nested array directly to another external function call or use `abi.encode` on it.
> 

Ref: [https://blog.soliditylang.org/2022/05/18/solidity-0.8.14-release-announcement/](https://blog.soliditylang.org/2022/05/18/solidity-0.8.14-release-announcement/)

[https://blog.soliditylang.org/2022/05/17/calldata-reencode-size-check-bug/](https://blog.soliditylang.org/2022/05/17/calldata-reencode-size-check-bug/)

This vulnerability can be misused since the function `queueTransaction`, `cancelTransaction`, `executeTransaction`, and `_getTxHash` has applicable conditions.

This is a similar issue of Code4rena
https://github.com/code-423n4/2022-06-putty-findings/issues/348

## Code Snippet
https://github.com/sherlock-audit/2022-11-frankendao/blob/main/src/Executor.sol#L2
```solidity
pragma solidity ^0.8.13;

contract Executor is IExecutor, FrankenDAOErrors {
	/* ... */
	bytes32 txHash = keccak256(abi.encode(_target, _value, _signature, _data, _eta));
	/* ... */
}
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-frankendao-judging/issues/62_
