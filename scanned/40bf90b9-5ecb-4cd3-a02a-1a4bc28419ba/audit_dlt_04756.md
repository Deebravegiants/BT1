# [M] Auctions that don't sell out set auction.lastPrice64x64 to incorrect value

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-09-knox
Published: 2022-10-18
Source: https://github.com/sherlock-audit/2022-09-knox-judging/issues/73
Type: sherlock-finding

## Details
0x52

medium

# Auctions that don't sell out set auction.lastPrice64x64 to incorrect value

## Summary

Vaults that don't sell out should price all sold options at the minimum auction price but instead they set the final price to the lowest price specified by filled orders.

## Vulnerability Detail

    function _finalizeAuction(
        AuctionStorage.Layout storage l,
        AuctionStorage.Auction storage auction,
        uint64 epoch
    ) internal {
        if (_processOrders(l, epoch) || block.timestamp > auction.endTime) {
            auction.status = AuctionStorage.Status.FINALIZED;
            emit AuctionStatusSet(epoch, auction.status);
        }
    }

When an auction fails to sellout by the end of the auction period, it is finalized even if _processOrders returns false. When _processOrders returns false it executes the following lines:

    auction.lastPrice64x64 = lastPrice64x64;
    auction.totalContractsSold = totalContractsSold;
    return false;

This sets the final price of the auction to the price of the last order that was filled. This is problematic because a dutch auction should set the final price to the minimum auction price not the lowest price offered. When the auction ended the price would have been at the minimum auction price.

## Impact

Buyers are overcharged if the auction ends without selling out

## Code Snippet

[AuctionInternal.sol#L359-L416](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L359-L416)

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-09-knox-judging/issues/73_
