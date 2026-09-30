# [M] Usage of transfer() may revert.

## Summary
Severity: Medium
Reporter: Nyx
Source: https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/lib/UniversalERC20.sol#L22-L34
Type: audit-issue

## Details
# Usage of transfer() may revert.

## Summary
transfer() uses a fixed amount of gas, which was used to prevent reentrancy. However this limit your protocol to interact with others contracts that need more than that to process the transaction.
## Vulnerability Detail
Specifically, the withdrawal will inevitably fail when: 

1.The withdrawer smart contract does not implement a payable fallback function. 
2.The withdrawer smart contract implements a payable fallback function which uses more than 2300 gas units. 
3.The withdrawer smart contract implements a payable fallback function which needs less than 2300 gas units but is called through a proxy that raises the call’s gas usage above 2300.
## Impact
transfer() uses a fixed amount of gas, which can result in revert.
## Code Snippet
https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/lib/UniversalERC20.sol#L22-L34

https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L152

https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L489
## Tool used

Manual Review

## Recommendation
Use call instead of transfer().
