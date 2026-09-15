# [H] User can place limit order before the auction started to manipulate the order price

## Summary
Severity: High
Reporter: ctf_sec
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L97-L107
Type: audit-issue

## Details
# User can place limit order before the auction started to manipulate the order price

## Summary

User can place limit order before the auction started to manipulate the order price

## Vulnerability Detail

when the smart contract validate the market order,

the code uses a modifier_marketOrdersAllowed

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L97-L107

in the function, it check if the auction started and if the auction has not ended.

however, when validating limit order, the function does not check if the auction has started.

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L82-L90

the check 

```solidity
_auctionHasStarted(auction);
```

is missing. So user can place limit order before the auction started.

## Impact

Allowing the user to place limit order can allow malicious actor to spoof the order price.

They are basically set the price before anyone elses, 

Or they can create spam order which then cancel later to manipulate the order price.

## Code Snippet

## Tool used

Manual Review

## Recommendation

We recommand add the _auctionHasStarted inside the funtion _limitOrderAllowed

```solidity
    function _limitOrdersAllowed(AuctionStorage.Auction storage auction)
        internal
        view
    {
        require(
            AuctionStorage.Status.INITIALIZED == auction.status,
            "status != initialized"
        );
        _auctionHasStarted(auction);
        _auctionHasNotEnded(auction);
    }
```
