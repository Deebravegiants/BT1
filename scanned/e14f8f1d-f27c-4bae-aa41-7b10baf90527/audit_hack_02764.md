# [M] depositToActiveBalance, initialStake don't work with fee-on transfer tokens

## Summary
Severity: Medium
Reporter: Bnke0x0
Source: https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/Sherlock.sol#L545
Type: audit-issue

## Details
# depositToActiveBalance, initialStake don't work with fee-on transfer tokens

## Summary

## Vulnerability Detail
There are ERC20 tokens that may make specific customizations to their ERC20 contracts. One type of these tokens is deflationary tokens that charge a specific fee for every transfer() or transferFrom(). Others are rebasing tokens that increase in value over time like Aave's tokens (balanceOf changes over time).

## Impact
The SherlockProtocolManager and sherlock's depositToActiveBalance() and initialStake  functions transfer _amount to this contract using 'token.safeTransferFrom(msg.sender, address(this), _amount);.This could have a fee, and less than _amount that ends up in the contract. will then try to transfer more than this contract actually has and will revert the transaction.

## Code Snippet
https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/Sherlock.sol#L545

        'token.safeTransferFrom(msg.sender, address(this), _amount);'

https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/managers/SherlockProtocolManager.sol#L769

      'token.safeTransferFrom(msg.sender, address(this), _amount);'

## Tool used

Manual Review

## Recommendation
One possible mitigation is measuring the asset change before and after the asset-transferring routines.
