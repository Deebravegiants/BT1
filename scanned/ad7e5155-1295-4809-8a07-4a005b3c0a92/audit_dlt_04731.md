# [H] `AuctionInternal._previewWithdraw()` might return the wrong result after some orders are removed during the withdrawal.

## Summary
Severity: High
Chain: Smart contract
Component: 2022-09-knox
Published: 2022-10-18
Source: https://github.com/sherlock-audit/2022-09-knox-judging/issues/141
Type: sherlock-finding

## Details
hansfriese

high

# `AuctionInternal._previewWithdraw()` might return the wrong result after some orders are removed during the withdrawal.

## Summary
`AuctionInternal._previewWithdraw()` might return the wrong result after some orders are removed during the withdrawal.

## Vulnerability Detail
- The auction state will be changed to `FINALIZED` and `PROCESSED` when `totalContractsSold` is greater than `auction.totalContracts` [here](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L391).

```solidity
if (totalContractsSold + data.size >= totalContracts) {
    auction.lastPrice64x64 = data.price64x64;
    auction.totalContractsSold = totalContracts;
    return true;
}
```
- When several users added orders with the same `price64x64`, the earlier user will be selected because the later users will be added in the right subtree [here](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/OrderBook.sol#L214-L221).

```solidity
// The new order belongs in the right subtree
if (price64x64 <= currentOrder.data.price64x64) {
    if (currentOrder.right == 0) {
        currentOrder.right = id;
    }
    currentOrder = index.orders[currentOrder.right];
    continue;
}
```

Currently, `_previewWithdraw()` removes the order during the withdrawal but it might return the wrong result after some orders are removed.

- Let's assume `auction.totalContracts = 10` and 2 users added limit orders.
- First, a user `Alice` added 1 limit order, `Order1 = {price64x64 = 80, size = 6}`.
- A user `Bob` added 2 limit orders. `Order2 = {price64x64 = 100, size = 6}`, `Order3 = {price64x64 = 80, size = 4}`.
- After the auction is started, it will be finalized at price 80 from [_processOrders()](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L359).

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-09-knox-judging/issues/141_
