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

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-09-knox-judging/issues/69_
