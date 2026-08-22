# [M] Traders might get unwanted results due to partially filled of orders

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-opyn
Published: 2022-12-03
Source: https://github.com/sherlock-audit/2022-11-opyn-judging/issues/196
Type: sherlock-finding

## Details
hansfriese

medium

# Traders might get unwanted results due to partially filled of orders

## Summary

During the auctions, the traders sign orders (buying/selling SQTH) with quantity specified but it is possible for auctions to partially fill these orders. This might be not what the traders wanted when they signed the order.

## Vulnerability Detail

Across the protocol, `Order` structure is used to represent the position of the traders for both selling and buying SQTH.
These orders are signed by the trader with an unused nonce.

```solidity
/// @dev order struct for a signed order from market maker
struct Order {
    uint256 bidId;
    address trader;
    uint256 quantity;
    uint256 price;
    bool isBuying;
    uint256 expiry;
    uint256 nonce;
    uint8 v;
    bytes32 r;
    bytes32 s;
}
```

Looking at the actual auction functions, it is possible that these orders are partially filled and that nonce is set to used.

```solidity
// #L491
function depositAuction(DepositAuctionParams calldata _p) external onlyOwner {
    ...
    // step 1 get all the eth in
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-opyn-judging/issues/196_
