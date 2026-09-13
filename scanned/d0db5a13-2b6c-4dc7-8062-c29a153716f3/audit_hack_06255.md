# [H] Anti-sniping mechanism enables auctions to go on for a long time, enabling attacks based on late-deposits

## Summary
Severity: High
Reporter: jkoppel
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L160
Type: audit-issue

## Details
# Anti-sniping mechanism enables auctions to go on for a long time, enabling attacks based on late-deposits

## Summary

Late bids to an auction extend the length of the auction by 15 minutes. This can be done an arbitrary number of times until the attacker runs out of capital. No other auctions may be run in the meantime. At the end of this, the attacker will get a new deposit on the vault.

This is very expensive and of limited use on its own. However, combined with https://github.com/sherlock-audit/2023-02-fair-funding-jkoppel/issues/5 , this allows any sufficiently-capitalized user to steal the deposits of all other users.

## Vulnerability Detail

The requirement that the bid increase by 2% every 15 minutes translates to an increase of 6.7x per day, so there is a limit to how long this delay can be, even with a very low starting bid.

In the extreme case, with a minimum starting bid of 1e-14 WETH, an attacker can prolong the auction by 21 days for "only" 2177 WETH. Depending on how much else is in the vault and how fast claims are expected, this may be enough to let them steal a lot.

## Impact

1. An attacker can use this to make a deposit 

2. A griefer (who expects to get his deposit back in a timely fashion) can delay or prevent other tokens from being auctioned for a while

## Code Snippet

See the anti-sniping mechanism at  https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L160 

It can be invoked an arbitrary number of times.

## Tool used

Manual Review

## Recommendation

Cap the number of times an auction may be extended.
