# [M] No `deadline` parameter in `MeritDutchAuction.mint` function

## Summary
Severity: Medium
Reporter: AkshaySrivastav
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128
Type: audit-issue

## Details
# No `deadline` parameter in `MeritDutchAuction.mint` function

## Summary
`MeritDutchAuction.mint` function does not take any deadline value as input due to which a user's txn can get mined significantly into the future.

## Vulnerability Detail
The gas prices of Ethereum network can fluctuate significantly due to which an NFT minter's transaction can stay in a pending state in the mempool. This pending txn will get executed when network's gas price reduces back to closer to the user's offered gas price. 

As the price of NFTs can reduce significantly with time, the price at which a user agreed to buy the NFT can differ significantly to the actual minting price when the txn gets executed.

A valid example of this would be:
- The protocol currently allows minting of NFTs even after the auction ends at `endPrice`.
- Alice wants to mint the NFT but only if the auction has not ended.
- She submits the txn but the txn stays in pending state. This duration could be minutes, hours or even longer.
- In the meanwhile, the auction ends and the price of NFT drops to `endPrice`.
- As the gas price of Alice's txn becomes favourable to network, her txn gets executed.

Here, the outcome resulted in Alice minting the NFT at a timestamp and price on which she didn't agree upon in the first place. 

## Impact
The `mint` transaction of users can get executed at a later point in future, forcing users to mint NFTs at a price that they didn't choose.

Note: It is totally possible that some users get interested in minting NFT only for the auction duration and then loose interest completely once the auction is over. 

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128

## Tool used

Manual Review

## Recommendation
Consider adding a deadline input parameter in the `mint` function beyond which the user's txn simply gets reverted.
