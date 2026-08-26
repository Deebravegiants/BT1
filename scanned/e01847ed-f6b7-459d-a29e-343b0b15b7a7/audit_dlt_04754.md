# [M] User unable to withdraw at the end of an auction if the order they placed is the same as clearing price, but did not receive any fills.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-09-knox
Published: 2022-10-18
Source: https://github.com/sherlock-audit/2022-09-knox-judging/issues/79
Type: sherlock-finding

## Details
yixxas

high

# User unable to withdraw at the end of an auction if the order they placed is the same as clearing price, but did not receive any fills.

## Summary
Users will be unable to call `withdraw()` if they place an order, and the price set is the same as the clearing price, but yet did not receive a fill as contracts sold have already reached 100% utilisation.

## Vulnerability Detail
Before withdrawing, `_previewWithdraw()` is called. On L317, we have `uint256 remainder = auction.totalContracts - totalContractsSold`. This assumes that `auction.totalContracts >= totalContractsSold`, which is not always true in this case due to how `totalContractsSold` is calculated. I will illustrate this with a simple example.

Assume,
`auction.totalContracts = 10`

Alice first `addLimitOrder()` with `price = 10`, `size = 10`.
Bob then `addLimitOrder()` with `price = 10`, 'size = 1'.
Bob calls `addLimitOrder()` again with `price = 10`, 'size = 1'.

Now order book have 3 orders.

`processOrder()` is then called, since utilisation reaches a 100%, clearing price is set to 10 and all contracts are sold to Alice.
Now, Bob is supposed to be able to call `withdraw()` and get only refund, since he did not receive any fills.

In `previewWithdraw()`, order book is looped through, and when `i = 3`, `totalContractsSold = 11`, since previous entries `data.size` is added to it. But it still enters the `if (data.price64x64 >= lastPrice64x64)` check since `data.price64x64 == lastPrice64x64`. Function will then revert at `uint256 remainder = auction.totalContracts - totalContractsSold` since `auction.totalContracts = 10` < `totalContractsSold = 11`.


## Impact
Users will be unable to withdraw their funds if their price offered is the same as clearing price and the orders before them does not withdraw.

## Code Snippet

[AuctionInternal.sol#L279-L347](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L279-L347)
```solidity
    function _previewWithdraw(
        AuctionStorage.Layout storage l,
        bool isPreview,
        uint64 epoch,
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-09-knox-judging/issues/79_
