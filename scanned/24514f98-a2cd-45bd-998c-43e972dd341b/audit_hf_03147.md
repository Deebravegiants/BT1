# [H] SurplusAuction.sol#closeAuction()will revert as

## Summary
Severity: High
Contest weight: 0.7527
Dataset id: 17666
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
SurplusAuction.sol#closeAuction() will revert at L173 as FDT can not transfer to the zero address.
See L173, token.transfer() with address(0) as to is not allowed.
https://github.com/fiatdao/fiat/blob/b8406c29638b9f6e598ad6d961583df5b0a719a5/src/auctions/SurplusAuction.sol#L165-L175
```solidity
function closeAuction(uint256 auctionId) external override {
    if (live == 0) revert SurplusAuction__closeAuction_notLive();
    if (
        !(auctions[auctionId].bidExpiry != 0 &&
        (auctions[auctionId].bidExpiry < block.timestamp ||
        auctions[auctionId].auctionExpiry < block.timestamp))
    ) revert SurplusAuction__closeAuction_notFinished();
    codex.transferCredit(address(this), auctions[auctionId].recipient,
    auctions[auctionId].creditToSell);
    token.transfer(address(0), auctions[auctionId].bid);
    delete auctions[auctionId];
}
```
SurplusAuction.sol#closeAuction() always reverts.

## Recommendation
token should be sent to the governance address instead:
```solidity
function closeAuction(uint256 auctionId) external override {
    if (live == 0) revert SurplusAuction__closeAuction_notLive();
    if (
        !(auctions[auctionId].bidExpiry != 0 &&
        (auctions[auctionId].bidExpiry < block.timestamp ||
        auctions[auctionId].auctionExpiry < block.timestamp))
    ) revert SurplusAuction__closeAuction_notFinished();
    codex.transferCredit(address(this), auctions[auctionId].recipient,
    auctions[auctionId].creditToSell);
    token.transfer(governance, auctions[auctionId].bid);
    delete auctions[auctionId];
}
```
