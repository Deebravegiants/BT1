# [M] User can get cheapest possible price by waiting and frontrunning other last mint transaction

## Summary
Severity: Medium
Reporter: shogoki
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128
Type: audit-issue

## Details
# User can get cheapest possible price by waiting and frontrunning other last mint transaction

## Summary

In a Dutch Auction like this, a user can wait to get a better price by taking the risk that the NFT is sold out (mint cap reached), but this risk can be mitigated here.

## Vulnerability Detail

The Dutch Auction plays on the concept that every user has the chance to get a better price by waiting, but nobody knows if other users already buy and the NFT reaches its cap. However on the blockchain all transactions are public and even the mempool can be monitored to see future transactions. A user can therefore always get the best price for the NFT, by waiting and monitoring the mempool. 
if the last transaction comes in, he can frontrun the call to mint and mint the tokens for the „latest“ price to himself.

## Impact

User can ensure to always get the best price.
Last user gets frontrunned and is not receiving NFTs

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128

## Tool used

Manual Review

## Recommendation

n/a
