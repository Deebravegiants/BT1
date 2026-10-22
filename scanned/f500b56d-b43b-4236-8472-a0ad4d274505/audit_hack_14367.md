# [M] Users have no control over the minted tokenIds

## Summary
Severity: Medium
Reporter: AkshaySrivastav
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128
Type: audit-issue

## Details
# Users have no control over the minted tokenIds

## Summary
The users who mint the NFT using `MeritDutchAuction` contract have no control over the token ids minted for them.

## Vulnerability Detail
By definition, NFTs are non-fungible tokens so each token can be significantly different than other tokens in features and monetary worth.

The `MeritDutchAuction.mint` does not let users choose the NFT id that they want to mint. The tokenIds minted to a user is simply determined by the total number of NFTs minted already (`minted` parameter).

This can lead to users getting different NFT ids than they originally chose to mint.

Consider this scenario:
- Alice & Bob want to mint `NFT#1111`.
- They both monitor the `MeritDutchAuction` contract and once `1110` NFTs gets minted they submit their `mint` txns.
- Bob's txn gets executed first so he gets the `NFT#1111`.
- Alice's txn gets executed next and she gets `NFT#1112`.

In this scenario, an undesired NFT gets minted to Alice even when she wanted to mint a different NFT. Alice also had to pay a similar price as `NFT#1111` for `NFT#1112`.

Note: The reason for a user for choosing to mint a specific NFT could be because of the some specific attributes of that particular NFT id. This behaviour is very common.

## Impact
Significantly different NFTs can get minted to users, much different than the NFTs that those users wanted to mint originally.

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128

## Tool used

Manual Review

## Recommendation
Consider adding a mechanism for users to choose and mint a specific token id, and revert if that particular token id is not available for minting.
