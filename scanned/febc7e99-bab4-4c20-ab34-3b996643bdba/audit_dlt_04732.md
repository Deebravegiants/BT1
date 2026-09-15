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
    AuctionStorage.Layout storage l,
    bool isPreview,
    uint64 epoch,
    address buyer
) private returns (uint256, uint256) {
    AuctionStorage.Auction storage auction = l.auctions[epoch];
    OrderBook.Index storage orderbook = l.orderbooks[epoch];

    uint256 refund;
    uint256 fill;

    int128 lastPrice64x64 = _clearingPrice64x64(auction);

    uint256 totalContractsSold;
    uint256 next = orderbook._head();
    uint256 length = orderbook._length();

    // traverse the order book and return orders placed by the buyer
    for (uint256 i = 1; i <= length; i++) {
        OrderBook.Data memory data = orderbook._getOrderById(next);
        next = orderbook._getNextOrder(next);

        if (data.buyer == buyer) {
            if (
                lastPrice64x64 < type(int128).max &&
                data.price64x64 >= lastPrice64x64
            ) {
                // if the auction has not been cancelled, and the order price is greater than or
                // equal to the last price, fill the order and calculate the refund amount
                uint256 paid = data.price64x64.mulu(data.size);
                uint256 cost = lastPrice64x64.mulu(data.size);

                if (
                    totalContractsSold + data.size >= auction.totalContracts
                ) {
                    // if part of the current order exceeds the total contracts available, partially
                    // fill the order, and refund the remainder
                    uint256 remainder =
                        auction.totalContracts - totalContractsSold; //@audit-H1 underflow

                    cost = lastPrice64x64.mulu(remainder);
                    fill += remainder;
                } else {
                    // otherwise, fill the entire order
                    fill += data.size;
                }

                // the refund takes the difference between the amount paid and the "true" cost of
                // of the order. the "true" cost can be calculated when the clearing price has been
                // set.
                refund += paid - cost;
            } else {
                // if last price >= type(int128).max, auction has been cancelled, only send refund
                // if price < last price, the bid is too low, only send refund
                refund += data.price64x64.mulu(data.size);
            }

            if (!isPreview) {
                // when a withdrawal is made, remove the order from the order book
                orderbook._remove(data.id); //@audit-H2 withdraw order
            }
        }

        totalContractsSold += data.size;
    }

    return (refund, fill);
}
```

The below scenario shows such cases.
- Let's assume `auction.totalContracts = 10` and 2 users added limit orders.
- First, a user `Alice` added 1 limit order, `Order1 = {price64x64 = 80, size = 6}`.
- A user `Bob` added 2 limit orders. `Order2 = {price64x64 = 100, size = 6}`, `Order3 = {price64x64 = 80, size = 4}`.
- After the auction is started, it will be finalized at price 80 from [_processOrders()](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L359).
- So from [this part](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L392-L393), `auction.lastPrice64x64 = 80`, `auction.totalContractsSold = 10`.
- After that, the auction was processed and users are trying to withdraw their funds using `withdraw()`.
- Because `Alice` added the limit order earlier than `Bob`, she should have 4 of 10, `Bob` should have 6 of 10.
- But when `Bob` tries to withdraw the funds, orders will be checked by this order, `Order2{100}, Order1{80}, Order3{80}`
- So with the `Order3`, [this condition](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L302-L306) is true and it will try to calculate `remainder` [here](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L317-L318).
- But [this line](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L318) will revert because `auction.totalContracts = 10, totalContractsSold = 6 + 6 = 12` as the whole amount of `Order1` was added to `totalContractsSold` already.
- `_previewWithdraw()` might revert also with other auction states when users call the function to check their funds.

## Impact
In some cases, it would be impossible to withdraw funds after the auction is processed properly.

## Code Snippet
https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L312-L321

## Tool used
Manual Review

## Recommendation
We should change [this part](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L303-L306) like below.

```solidity
if (
    lastPrice64x64 < type(int128).max &&
    data.price64x64 >= lastPrice64x64 &&
    totalContractsSold < auction.totalContracts
) {
```


Duplicate of #106
