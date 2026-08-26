# [H] Limit orders with the same limit price can be abused to allow vault to oversell options

## Summary
Severity: High
Chain: Smart contract
Component: 2022-09-knox
Published: 2022-10-18
Source: https://github.com/sherlock-audit/2022-09-knox-judging/issues/70
Type: sherlock-finding

## Details
0x52

high

# Limit orders with the same limit price can be abused to allow vault to oversell options

## Summary

Limit orders allow a vault to become oversold which can lead to oversized losses for vault and potentially insolvency

## Vulnerability Detail

Limit orders are designed to allow users to enter in a predetermined price, but they can be abused to sell more contracts than intended. Overselling a vault can lead to oversized losses and insolvency if the the market moves too much against the vault.

Example:
There are 100 contracts for sale. A user creates 10 account. When the price is at 0.5 the user places a limit order on each account for 75 contract @ 0.25. Now the price drops below 0.25 the user calls Auction#finalizeAuction. This will trigger AuctionInternal#_processOrders. Since there are more than 100 contracts sold it will set the total number of contracts sold to 100 and set auction.lastPrice64x64 = 0.25. The issue is that now all 750 contracts bought in the limit orders will now be valid for withdraw, since each price = 0.25. Should the options end up being ITM the vault would be on the hook for potentially way more contracts than it should be. If all 750 contracts were bought by the same account the order would be partially filled but since each account made a separate order, each one is valid for withdrawal.

## Impact

Oversized losses and insolvency

## Code Snippet

[AuctionInternal.sol#L217-L254](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L217-L254)

## Tool used

Manual Review

## Recommendation

In AuctionInternal#_processOrders, explicitly check for additional orders with the same price as the final order. Add a new bool to the order struct and for all orders that share the same final price, change the bool to true indicating that they are overflow orders. When calling AuctionInternal#_previewWithdraw, check this bool and automatically refund these orders.
