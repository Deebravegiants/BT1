# [M] `MeritNFT.sol` does not fully implemented erc721enumerable

## Summary
Severity: Medium
Reporter: imkapadia
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L10
Type: audit-issue

## Details
# `MeritNFT.sol` does not fully implemented erc721enumerable

## Summary
`MeritNFT` contract does not fully implement the ERC721Enumerable interface, which allows for enumeration and querying of token ownership and token IDs. While it does inherit the ERC721 Enumerable contract. This incomplete implementation may lead to unexpected behavior and limited functionality for applications and users relying on the ERC721Enumerable standard.

## Vulnerability Detail
The contract is missing the necessary functions and data structures to fully comply with the ERC721Enumerable interface. The ERC721Enumerable interface extends the ERC721 standard and adds additional functions to support enumeration of token IDs and querying token ownership.

The following functions are required by the ERC721Enumerable interface but are missing in the contract:

`tokenByIndex(uint256 _index)`: This function should return the token ID at a given index in the list of all tokens.
`tokenOfOwnerByIndex(address _owner, uint256 _index)`: This function should return the token ID owned by a specific address at a given index.

## Impact
The incomplete implementation of ERC721Enumerable prevents applications and users from utilizing the full functionality provided by the ERC721Enumerable interface. This may restrict the ability to perform efficient token enumeration, query token ownership, and build robust applications relying on these features.

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L10

## Tool used

Manual Review

## Recommendation
Implement the missing functions `tokenByIndex()`, and `tokenOfOwnerByIndex()` as specified by the ERC721Enumerable interface.
Ref: https://eips.ethereum.org/EIPS/eip-721
