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

    address public proxyAddr1 = address(4);
    address public proxyAddr2 = address(5);
    ERC20Mock public token;


function setUp() public {
      vm.label(owner, "owner");
      vm.label(bob, "bob");
      vm.label(alice, "alice");
      vm.label(proxyAddr1, "proxy1");
      vm.label(proxyAddr2, "proxy2");

      dodoApprove = new DODOApprove();

      token = new ERC20Mock("Token", "tk");
      vm.label(address(token), "Token");
      token.transfer(alice, 100 * 10 ** 18);
    }

function testClaimTokensByNotProxyFail() public {
      dodoApprove.init(owner, bob);
      vm.prank(alice);
      token.approve(address(dodoApprove), type(uint256).max);
      vm.prank(bob);
      vm.expectRevert(bytes("DODOApprove:Access restricted"));
      dodoApprove.claimTokens(address(token), alice, bob, 50e18);
      assertEq(token.balanceOf(bob), 0);
    }
}
```

## Tool used

Manual Review

## Recommendation

Consider adding a check to  [init()](https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/DODOApprove.sol#L45-L48) or [claimTokens()](https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/DODOApprove.sol#L72-L82) and throw when the callee is not a contract.
