# [M] Auction could sell more contracts than auction.totalContracts

## Summary
Severity: Medium
Reporter: dipp
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L479-L489
Type: audit-issue

## Details
# Auction could sell more contracts than auction.totalContracts

## Summary

Limit orders may be made before the auction starts and thus the utilization of the auction is not checked. This would lead to the total contracts sold to be more than auction.totalContracts.

## Vulnerability Detail

When an order is added, ```_finalizeAuction``` is only called if the auction has started. The ```_finalizeAuction``` function will call the ```_processOrders``` function which will return true if the auction has reached 100% utilization. Since limit orders can be made before the start of an auction, ```_finalizeAuction``` is not called and any amount of new orders may be made.

## Impact

Selling more options than what the vault is able to cover might lead to temporarily stuck funds for users.

## Code Snippet

[AuctionInternal.sol#L479-L489](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L479-L489)
```solidity
    function _validateLimitOrder(
        AuctionStorage.Layout storage l,
        int128 price64x64,
        uint256 size
    ) internal view returns (uint256) {
        require(price64x64 > 0, "price <= 0");
        require(size >= l.minSize, "size < minimum");

        uint256 cost = price64x64.mulu(size);
        return cost;
    }
```

[AuctionInternal.sol#L545-L562](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L545-L562)
```solidity
    function _addOrder(
        AuctionStorage.Layout storage l,
        AuctionStorage.Auction storage auction,
        uint64 epoch,
        int128 price64x64,
        uint256 size,
        bool isLimitOrder
    ) internal {
        l.epochsByBuyer[msg.sender].add(epoch);

        uint256 id = l.orderbooks[epoch]._insert(price64x64, size, msg.sender);

        if (block.timestamp >= auction.startTime) {
            _finalizeAuction(l, auction, epoch);
        }

        emit OrderAdded(epoch, id, msg.sender, price64x64, size, isLimitOrder);
    }
```

## Tool used

Manual Review

## Recommendation

The orders for an auction should be checked before the auction starts. In ```_addOrder```, add a condition that will call ```_processOrders``` if the auction has not started yet. If ```_processOrders``` returns true then do not allow the order to be added. Or just allow the auction to be finalized before it starts if the total contracts sold has reached the auction's totalContracts.
