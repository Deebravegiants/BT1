# [M] 0 size order is allowed in Auction.sol

## Summary
Severity: Medium
Reporter: ctf_sec
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/Auction.sol#L175
Type: audit-issue

## Details
# 0 size order is allowed in Auction.sol

## Summary

0 size order is allowed in Auction.sol

then user can create a lot of spam order at no cost to take storage space in orderbook.
and affect order matching.

## Vulnerability Detail


0 size order is allowed in Auction.sol

When we add limit order or market order in the auction, the logic valid the order and return a cost.

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/Auction.sol#L175

there is no check to revert the transaction when order size is 0

inside the function _validateLimitOrder, the function valid the if order size >= l.minSize

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L479-L489

there is no check to revert the transaction when order size is 0, either.

If the order size is 0, the cost would also be 0.

where is l.minSize set?

l.minSize is set in the AuctoinProxy.sol

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionProxy.sol#L20-L30

there is no check to revert the transaction when minSize is 0.

## Impact

then user can create a lot of spam order at no cost to take storage space in orderbook.
and affect order matching if 0 order is allowed.

in the function _previewWith, the function needs to traverse the order, the spam order would increase the gas cost

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L293-L303

## Code Snippet

## Tool used

Manual Review

## Recommendation

We recommend the project add check to make sure 0 size order is now allowed.

we can added 

```solidity
  require(minSize > 0, 'invalid order size');
```

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionProxy.sol#L20-L30
