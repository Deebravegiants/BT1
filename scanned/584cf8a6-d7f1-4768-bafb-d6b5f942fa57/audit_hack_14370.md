# [M] Block griefing attack can be used to mint NFT cheaply

## Summary
Severity: Medium
Reporter: AkshaySrivastav
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L116-L122
Type: audit-issue

## Details
# Block griefing attack can be used to mint NFT cheaply

## Summary
A block space griefing attack can be performed on the EVM chain to get NFTs at a cheaper price.

## Vulnerability Detail
As the price of NFTs in the auction contract decays with time. An attacker can forcefully occupy the block space for a duration of time to prevent others from minting NFTs and then can buy the NFTs at a decayed price.

Scenario:
- Auction contract is set to mint NFTs for a duration of 30 minutes. Starting price 50 ETH & ending price 20 ETH. Step size 10 minutes
- Attacker can submits a large number of txns to the network with gas prices greater than normal user's mint txns.
- The griefing lasts for 10 minutes, the price decays.
- Now the attacker stops the griefing and buys some or all NFTs at 40 ETH price.

Note, it is not the case that the attacker must always perform griefing for 10 minutes, in case 8 minutes have already passed then the attacker can only perform griefing for 2 minutes and can get a discount of 10 ETH.

## Impact
As the price decays with time, block space griefing attack can be used to mint NFT cheaply.

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L116-L122

## Tool used

Manual Review

## Recommendation
Consider adding a minimum duration parameter for auction duration and stepsize so that the auctions stays active without decay for longer durations. As the time duration increases, the attack becomes difficult to perform.
