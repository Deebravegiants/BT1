# [M] CAP_PER_ADDRESS doesn't provide real protection

## Summary
Severity: Medium
Reporter: 0xeix
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L12
Type: audit-issue

## Details
# CAP_PER_ADDRESS doesn't provide real protection

## Summary

In MeritDutchAuction, there is a variable that defines how many NFTs can one address owns. However, this can be easily bypassed.

## Vulnerability Detail

As there are many people who have multiple addresses, the problem with bypassing this restriction arises. It doesn't create any real protection and that's not a good practice to restrict the number of NFTs that can be minted by one address. This will basically lead to the situation where only few people minted almost all NFTs.

## Impact

CAP_PER_ADDRESS can be bypassed and few address can mint all NFTs.

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L12
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L143

## Tool used

Manual Review

## Recommendation

Remove CAP_PER_ADDRESS variable as it's not a good protection again centralization.
