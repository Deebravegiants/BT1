# [M] Owner can run the Dutch auction untruthfully

## Summary
Severity: Medium
Reporter: alexxander
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128
Type: audit-issue

## Details
# Owner can run the Dutch auction untruthfully

## Summary
Owner can game the Dutch auction by purchasing some NFTs early and artificially inflating the perceived value of the NFTs.

## Vulnerability Detail
Auctions in general are used when the underlying item(s) for auction don't have a clear market value. During the auction the bidders(users) usually receive some kind of "signals" that they then interpret to estimate what the value of the asset for auction is - this includes private signals i.e some kind of estimation/research that the user did about the item of the auction, but also includes public signals - the actions of other participants in the auction (the price they bid/paid or the amount of items they bought). An example of a signal would be when the user is waiting for a later period to mint NFTs at a lower price point, however, he suddenly sees an increased demand and now he perceives that it is too great of a risk to wait for the desired price point (since there might be no NFTs left considering the increased demand) and decides to purchase at a higher price point. The implemented Merit Dutch auction, consisting of multiple items for sale at the same time, is susceptible to being gamed where the owner purchases some quantity of items (NFTs) in the early stages of the auction, therefore, artificially inflating the demand and perceived value of the items. The current implementation of the mint function also allows for a fallback() to be configured that can invoke preset contracts to mint NFTs, therefore, bypassing the CAP_PER_ADDRESS restriction in a single transaction. Lastly, since the owner can also withdraw all funds, he can run such an untruthful auction at a minimal cost.

- Reference - 
A recent research paper [link](https://people.eecs.berkeley.edu/~ksk/files/GDA.pdf), that reviews in-depth GDAs (Gradual Dutch Auctions) in the context of NFT sales, discusses a similar untruthful run where the owner games the auction by participating himself early on.


## Impact
Fairness of the auction is undermined.

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128
## Tool used

Manual Review

## Recommendation
Implement a whitelist to restrict which addresses can participate. Owner of the NFT shouldn't be able to mint after the auction starts.
