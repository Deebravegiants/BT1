# [H] AuctionInternal#_previewWithdraw can cease to function if user has multiple partially filled/unfilled orders

## Summary
Severity: High
Chain: Smart contract
Component: 2022-09-knox
Published: 2022-10-18
Source: https://github.com/sherlock-audit/2022-09-knox-judging/issues/69
Type: sherlock-finding

## Details
0x52

high

# AuctionInternal#_previewWithdraw can cease to function if user has multiple partially filled/unfilled orders

## Summary

AuctionInternal#_previewWithdraw contains an accounting error that causes it to underflow and revert if the user has multiple large partially filled/unfilled orders. The underflow will cause the user's funds to become stuck as _withdraw will always fail due to the revert in _previewWithdrawal

## Vulnerability Detail

    for (uint256 i = 1; i <= length; i++) {
        OrderBook.Data memory data = orderbook._getOrderById(next);
        next = orderbook._getNextOrder(next);

        if (data.buyer == buyer) {
            if (
                lastPrice64x64 < type(int128).max &&
                data.price64x64 >= lastPrice64x64
            ) {
                uint256 paid = data.price64x64.mulu(data.size);
                uint256 cost = lastPrice64x64.mulu(data.size);

                if (
                    totalContractsSold + data.size >= auction.totalContracts
                ) {
                    uint256 remainder =
                        auction.totalContracts - totalContractsSold;

                    cost = lastPrice64x64.mulu(remainder);
                    fill += remainder;
                } else {
                    fill += data.size;
                }
                refund += paid - cost;
            } else {
                refund += data.price64x64.mulu(data.size);
            }
            if (!isPreview) {
                orderbook._remove(data.id);
            }
        }
        totalContractsSold += data.size;
    }

The loop shown above cycles through the all the orders in the epoch and fills or refunds orders for the buyer. The specific section we want to focus on is for orders that are above the last price but either partially filled or unfilled. In this scenario, filled will be increases by the remainder but totalContractsSold will be increases by data.size. Since totalContractsSold + data.size must be greater than auction.totalContracts, after the first partially filled order totalContractsSold will now be greater than auctions.totalContracts. Now imagine that there is another order after. This order will cause an underflow which will revert the transaction. Since _previewWithdraw is called each time _withdraw is called, it will now become impossible for the user to withdraw their funds. With only market orders it would be impossible for a situation like this to arise but due to limit orders and the dutch auction it's possible for a user to have multiple orders partially filled/unfilled that are at or above the final auction price.

## Impact

User loss of funds

## Code Snippet

[AuctionInternal.sol#L279-L347](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L279-L347)

## Tool used

Manual Review

## Recommendation

When an order is partially filled, it should increment totalContractsSold by remainder rather than data.size. This makes it impossible for an underflow to happen when calculating remainder

Duplicate of #106
