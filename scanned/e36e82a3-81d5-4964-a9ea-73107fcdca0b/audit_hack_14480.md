# [M] Potential Miner Manipulation Risk with block.timestamp in getPriceAt Function

## Summary
Severity: Medium
Reporter: pengun
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L101
Type: audit-issue

## Details
# Potential Miner Manipulation Risk with block.timestamp in getPriceAt Function

## Summary
The current getPriceAt function uses block.timestamp to determine the price, which can be manipulated by miners. This could potentially allow a malicious miner to set a higher timestamp on the boundary of a step to purchase at a lower price than expected, causing harm to the protocol.

## Vulnerability Detail
In Ethereum, block.timestamp can be manipulated by miners to some extent. In this scenario, a miner could influence the outcome of the getPriceAt function by manipulating the block timestamp to affect the step boundary.

This manipulation could potentially allow user purchase an asset at a lower price than expected, exploiting the protocol for their advantage. This could lead to losses for the protocol and other honest participants.

## Impact
Miner can make the protocol less profitable.

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L101

## Tool used

Manual Review

## Recommendation
Using block number instead of block timestamp. The block number is strictly incremental and cannot be influenced by miners.
