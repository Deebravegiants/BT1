# [M] The contract may revert as not enough WETH are present to refund last bidder

## Summary
Severity: Medium
Reporter: weeeh_
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L165-L167
Type: audit-issue

## Details
# The contract may revert as not enough WETH are present to refund last bidder

## Summary
If the contract runs out of WETH, for some reasons, and a new bidder does provide more amount than the last bidder, then the function will revert causing a denial of service.

## Vulnerability Detail
When a client does request a bid by calling `AuctionHouse.bid(id, amount)`, and the `amount` is greater than `self.highest_bid * (100 + MIN_INCREMENT_PCT) / 100`,  then the previous bidder should be refunded, if present. But if the contract does not have the amount of WETH to refund last bidder,  then the function will revert possibly causing a denial of service.

## Impact
The bid function is unavailable until last bidder is refunded.

## Code Snippet
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L165-L167

## Tool used
vim
Manual Review

## Recommendation
Before doing `ERC20(WETH).transfer` on last bidder, the contract should check its internal balance.
