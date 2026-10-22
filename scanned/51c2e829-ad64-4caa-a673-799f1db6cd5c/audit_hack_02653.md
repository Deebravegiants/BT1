# [M] Deflationary tokens are not supported

## Summary
Severity: Medium
Reporter: Bnke0x0
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L617-L621
Type: audit-issue

## Details
# Deflationary tokens are not supported

## Summary

## Vulnerability Detail
There are ERC20 tokens that may make certain customizations to their ERC20 contracts. One type of these tokens is deflationary tokens that charge a certain fee for every transfer() or transferFrom().

## Impact
assume that the external ERC20 balance of the contract increases by the same amount as the amount parameter of the transferFrom.

## Code Snippet
1. File: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L617-L621

         'IERC20(s.tokenIn).safeTransferFrom(
                msg.sender,
                address(Exchange),
                s.amountInMax
            );'

2. File: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/QueueInternal.sol#L229-L233

         'IERC20(s.tokenIn).safeTransferFrom(
                msg.sender,
                address(Exchange),
                s.amountInMax
            );'

## Tool used

Manual Review

## Recommendation
One possible mitigation is to measure the asset change right before and after the asset-transferring functions.
