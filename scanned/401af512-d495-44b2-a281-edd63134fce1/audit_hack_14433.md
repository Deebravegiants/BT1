# [M] Mint with `amount` set to `0` emits incorrect `Minted` event for offchain integrations

## Summary
Severity: Medium
Reporter: prott00n
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L167-L168
Type: audit-issue

## Details
# Mint with `amount` set to `0` emits incorrect `Minted` event for offchain integrations

## Summary
Contract `MeritDutchAuction` allows minting NFT tokens using `mint` function. It is possible to pass `0` as an `amount` parameter which will result in emitting incorrect event.

## Vulnerability Detail
Passing value `0` for an `amount` parameter in `mint` function will not mint any NFT tokens but will emit `Minted` event.

## Impact
This would be usually low severity issue but in this particular example it is stated that the event will be used for offchain integrations. Exploiting vulnerability it is possible to
- emit `Minted` event when the auction finished and all NFTs were minted
- emit `Minted` event without minting any NFTs
- emit `Minted` event when the NFT address was not correctly set

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L167-L168

## Tool used
Manual Review

## Recommendation
It is recommended to check that the passed value of `amount` is not equal to `0`.
