# [M] The user may not mint the NFT of the specified id because of frontrun

## Summary
Severity: Medium
Reporter: kutugu
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/ab734b575dc3b268de0457c2e3ab0e7d10cd7dd8/dutch-nft/src/MeritDutchAuction.sol#L128
Type: audit-issue

## Details
# The user may not mint the NFT of the specified id because of frontrun

## Summary

In Ethereum, due to the existence of frontrun, the user cannot mint the specified nft id, which may result in the user miss some high-value numbers of the nft.

## Vulnerability Detail

1. At present, 887 NFTs have been mint, and the next sequence will be 888
2. The User liked the number and mint, but was frontruned, resulting in mint 889
3. The user takes a loss because he only wants 888 and should not be mint if he misses it

## Impact

The user may not mint the NFT of the specified id because of frontrun

## Code Snippet

- https://github.com/sherlock-audit/2023-07-beam-auction/blob/ab734b575dc3b268de0457c2e3ab0e7d10cd7dd8/dutch-nft/src/MeritDutchAuction.sol#L128

## Tool used

Manual Review

## Recommendation

Allows the user to pass the specified id through the parameter, and not mint other NFTs if miss
