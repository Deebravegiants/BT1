# [M] [M-01] Users should be allowed to bid equal to the Bid-Increment (Prev Highest Bid + increment)

## Summary
Severity: Medium
Reporter: DevABDee
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L133
Type: audit-issue

## Details
# [M-01] Users should be allowed to bid equal to the Bid-Increment (Prev Highest Bid + increment)

## Summary

[AuctionHouse.bid()](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L133) doesn't allow bidders to bid equal to the Bid-Increment (Prev Highest Bid + increment)

## Vulnerability Detail

This check in the `AuctionHouse.bid()` function, will not gonna allow users to bid equal to the Bid-Increment
```vyper
assert _amount > self.highest_bid * (100 + MIN_INCREMENT_PCT) / 100 , "bid not high enough" 
```
Assume:
- `highest_bid` = `100` Tokens. 
- According to this formula `self.highest_bid * (100 + MIN_INCREMENT_PCT) / 100`, the least the next user can bid will be `102`
- However, if a bidder attempts to bid with exactly `102` Tokens, the function will reject their offer. Instead, they must bid at least `103` Tokens.
- This one token can make a big difference since the token in question is WETH

## Impact

- Will cost users some extra WETH (esp. the winner)

## Code Snippet

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L151 OR https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L151

## Tool used

Manual Review

## Recommendation
Use `>=` to make sure that users are allowed to bid equal to the Bid-Increment (Prev Highest Bid + increment)
```diff
- assert _amount > self.highest_bid * (100 + MIN_INCREMENT_PCT) / 100 , "bid not high enough"
+ assert _amount >= self.highest_bid * (100 + MIN_INCREMENT_PCT) / 100 , "bid not high enough" 
```
