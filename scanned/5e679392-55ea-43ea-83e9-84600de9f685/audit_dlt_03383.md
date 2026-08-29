# [H] Anyone can call onERC721Received() function and spam the array "nfts"

## Summary
Severity: High
Chain: Smart contract
Component: 2021-05-visorfinance
Published: 2021-05-19
Source: https://github.com/code-423n4/2021-05-visorfinance-findings/issues/66
Type: code-finding

## Details
# Handle

Sherlock


# Vulnerability details

## Impact
An attacker can deal direct economic damage to the owner/delegate spending some gas to spam the array of "nfts" with different values. It will be more costly to remove these nfts one-by-one, transaction-by-transaction. Also, it makes other functions dealing with "nfts" array more costly.

## Proof of Concept
Lines 519-520
function onERC721Received(address operator, address from, uint256 tokenId, bytes calldata) external override returns (bytes4) {
      _addNft(msg.sender, tokenId);

## Tools Used
Hardhat

## Recommended Mitigation Steps
To check in modifiers of ERC721Received () that only the owner or delegates can invoke this function. Revert if someone else calls.
