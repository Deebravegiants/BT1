# [H] Use of `transfer` and `transferFrom` without checking the return value

## Summary
Severity: High
Reporter: ck
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L164-L171
Type: audit-issue

## Details
# Use of `transfer` and `transferFrom` without checking the return value

## Summary

Use of `transfer` and `transferFrom` without checking the return value

## Vulnerability Detail

During bids `transfer` and `transferFrom` are used to perform token transfers. As per `ERC20.vy`, they return `True` on success.

The bidding process however doesn't check for this return value and failed transfers that don't revert would lead to breaking of the bidding process.

For instance, a failed `transfer` could lead to a bidder losing their refund.

## Impact

Bidding process will be broken and may lead to loss of funds.

## Code Snippet

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L164-L171

## Tool used

Manual Review

## Recommendation

Check the return values of `transfer` and `transferFrom` and revert if false.
