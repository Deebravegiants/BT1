# [H] In `Auction.sol`, users might fail to withdraw the funds from the processed auction because of the uint underflow.

## Summary
Severity: High
Chain: Smart contract
Component: 2022-09-knox
Published: 2022-10-18
Source: https://github.com/sherlock-audit/2022-09-knox-judging/issues/140
Type: sherlock-finding

## Details
hansfriese

high

# In `Auction.sol`, users might fail to withdraw the funds from the processed auction because of the uint underflow.

## Summary
In `Auction.sol`, users might fail to withdraw the funds from the processed auction because of the uint underflow.

## Vulnerability Detail
In `Auction.sol`, users might fail to withdraw the funds from the processed auction because of the uint underflow.

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

While withdrawing the funds after the auction is processed, it doesn't check the `totalContractsSold` properly in the [_previewWithdraw()](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L279) and users might fail to withdraw the funds as it reverts with the `uint` underflow.

```solidity
function _previewWithdraw(
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-09-knox-judging/issues/140_
