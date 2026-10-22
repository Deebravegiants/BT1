# [M] Queue deposits don't work with fee-on transfer tokens

## Summary
Severity: Medium
Reporter: Bnke0x0
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L103
Type: audit-issue

## Details
# Queue deposits don't work with fee-on transfer tokens

## Summary

## Vulnerability Detail
There are ERC20 tokens that may make specific customizations to their ERC20 contracts. One type of these tokens is deflationary tokens that charge a specific fee for every transfer() or transferFrom(). 

## Impact
The Queue 's deposit() function transfer 'amount - credited' to this contract using ERC20.safeTransferFrom(msg.sender, address(this), amount - credited);. This could have a fee and less than amount - credited that ends in the contract.

## Code Snippet
https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L103

         ' ERC20.safeTransferFrom(msg.sender, address(this), amount - credited);'

## Tool used

Manual Review

## Recommendation
One possible mitigation is measuring the asset change before and after the asset-transferring routines.
