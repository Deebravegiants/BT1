# [H] _previewWithdraw function in AuctionInternal.sol has unbounded gas consumption loop and can block user from withdraw

## Summary
Severity: High
Reporter: ctf_sec
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L212-L219
Type: audit-issue

## Details
# _previewWithdraw function in AuctionInternal.sol has unbounded gas consumption loop and can block user from withdraw

## Summary

_previewWithdraw function in AuctionInternal.sol has unbounded gas consumption loop and can block user from withdraw 

## Vulnerability Detail

in the code below, the _withdraw function call _previewWithdraw to estimate the withdraw amount.

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L212-L219

function _previewWithdraw traverses the orderbook and returns the refund and fill amounts,

however, if the orderbook have a lot of order, the gas may running out in the for loop below inside the function _previewWithdraw

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L291-L302

## Impact

the transaction may revert if gas is running out in _previewWithdraw, thus affect user withdraw.

## Code Snippet

## Tool used

Manual Review

## Recommendation

We recommend the project get rid of the unbounded loss inside the orderbook.
