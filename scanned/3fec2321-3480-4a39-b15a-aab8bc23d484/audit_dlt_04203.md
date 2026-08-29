# [M] DODOApprove.claimTokens() SHOULD CHECK IF THE CALLEE IS A CONTRACT

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-dodo
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/60
Type: sherlock-finding

## Details
Chandr

medium

# DODOApprove.claimTokens() SHOULD CHECK IF THE CALLEE IS A CONTRACT

## Summary

[claimTokens()](https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/DODOApprove.sol#L72-L82)  from [DODOApprove](https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/DODOApprove.sol#L21) contract sould check if calle is a contract


## Vulnerability Detail

If we [init()](https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/DODOApprove.sol#L45-L48) [DODOApprove](https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/DODOApprove.sol#L21) contract with wallet instead of proxy contract we could avoid [requirement()](https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/DODOApprove.sol#L78) in [claimTokens()](https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/DODOApprove.sol#L72-L82)


## Impact

We believe it’s not the desired behavior to call a non-contract address and consider it a successful call.


## Code Snippet
### Forge testcase
```solidity
// SPDX-License-Identifier: Unlicense

pragma solidity 0.8.16;

import "forge-std/Test.sol";
import "contracts/DODOApprove.sol";
import "./mocks/ERC20Mock.sol";

contract Zloychan is Test {
    DODOApprove public dodoApprove;
    address public owner = address(1);
    address public alice = address(2);
    address public bob = address(3);

```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/60_
