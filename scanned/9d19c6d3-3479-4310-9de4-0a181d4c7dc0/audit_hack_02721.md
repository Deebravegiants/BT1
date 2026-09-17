# [M] Price deviation in severe markets

## Summary
Severity: Medium
Reporter: __141345__
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L234-L250
Type: audit-issue

## Details
# Price deviation in severe markets

## Summary

The max and min prices for new auction is determined 2 hours prior to the auction begins. However if during the 2 hours, the market tumbles and the price moves far up or down, the generated prices would deviate far from the real market. The users of the vault might lose fund if not withdraw immediately.


## Vulnerability Detail

If for a put vault sell WBTC put, during the 2 hours between epoch initialization and auction begin, BTC prices drop 5%. The put price would deviate far from real market. If the owners of the vault are not aware of the situation and take action soon, the put option will be written soon. And the owners of the vault will be taken advantage of and lose fund.

## Impact

During severe market, some users will lose fund.


## Code Snippet

`_setAuctionPrices()` is called when new epoch is initialized, 2 hours before the auction starts.

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L234-L250


## Tool used

Manual Review


## Recommendation

Call `_setAuctionPrices()` when the auction starts instead of 2 hours prior. So the timely market condition could be reflected.
