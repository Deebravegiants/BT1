# [H] First minter can dos others by minting entire collection

## Summary
Severity: High
Reporter: p12473
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L169
Type: audit-issue

## Details
# First minter can dos others by minting entire collection

## Summary

For highly sought after NFT collections, the first minter can DOS others by minting the entire collection.

## Vulnerability Detail

The first minter with programming knowledge can:

1. monitor the mempool to frontrun any other mint transactions on the start block. This ensures (s)he gets the first mint since flashbots bundles are always at the top of a block.
2. use a smart contract to create multiple child smart contracts to mint the NFTs. The child smart contracts can be self-destructed later to refund some gas. This allows the first minter to bypass the `mintedPerAddress` check.
3. If 1 transaction is not enough to mint the entire collection, the first minter can bundle a few more transactions to ensure that he mints the entire collection. 

Once the entire auction has been minted by the first minter, he can resell it a secondary market for a higher price.

## Impact

Non-technical users will not be able to mint as they are unable to compete with these bots.

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L169

## Tool used

Manual Review

## Recommendation

- Consider using a [variable rate GDA](https://www.paradigm.xyz/2022/08/vrgda) instead of a basic dutch auction
