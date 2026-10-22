# [M] Auction will be permanently broken if early NFTs are manually minted.

## Summary
Severity: Medium
Reporter: thekmj
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L158
Type: audit-issue

## Details
# Auction will be permanently broken if early NFTs are manually minted.

## Summary

In the Merit NFT, there is no guarantee that the Auction contract is the only one with the MINTER role. The admin may want to mint early NFTs for any reasons (e.g. lucky draw, airdrop, etc).

## Vulnerability Detail

Note that Merit NFT uses OpenZeppelin's Access Control Enumerable, which allows multiple addresses per role.

Since `MeritDutchAuction` attempts to mint sequential-ID NFTs, anyone with the MINTER role can permanently break auction by minting in advance the NFT with ID 1, or the one they desire. Then `MeritDutchAuction.mint()` will always revert due to attempting to mint already-existent NFTs.

## Impact

If early-ID NFTs are minted for any reason, auction will be bricked.

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L158

## Tool used

Manual Review

## Recommendation

There are several solutions around this issue:
- Ensure before starting auction that the auction contract is the only one that's granted the MINTER role.
- Allow users to manually select NFTs to buy, instead of minting strictly sequential IDs.
