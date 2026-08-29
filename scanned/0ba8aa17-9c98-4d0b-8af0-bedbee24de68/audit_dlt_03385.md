# [H] Denial of service for NFT's

## Summary
Severity: High
Chain: Smart contract
Component: 2021-05-visorfinance
Published: 2021-05-17
Source: https://github.com/code-423n4/2021-05-visorfinance-findings/issues/16
Type: code-finding

## Details
# Handle

gpersoon


# Vulnerability details

## Impact
The function _removeNft uses more gas as more NFT's are added.
An attacker can send random NFT's to the contract, which are received via onERC721Received.
This functions adds the NFT's to the array nfts, using the function _addNft.
The longer the nfts array, the more gas is used by the function _removeNft, which is called from transferERC721 &  timeUnlockERC721.
I tried the proof concept below in Remix, and noticed the required amount of gas increased with about 3000 per NFT.
So with enough NFT's you get an out of gas error in _removeNft and thus the functions transferERC721 &  timeUnlockERC721 will no longer work.

## Proof of Concept
 function onERC721Received(address operator, address from, uint256 tokenId, bytes calldata) external override returns (bytes4) {
      _addNft(msg.sender, tokenId);
      return IERC721Receiver.onERC721Received.selector;
    }

// Test gas usage
pragma solidity ^0.8.0;
contract test {    
    struct Nft {
      uint256 tokenId; 
      address nftContract;
    }

    Nft[] public nfts;
    
     function _addNft(address nftContract, uint256 tokenId) public {
      nfts.push(Nft({tokenId: tokenId,nftContract: nftContract}));
    }

    function _removeNft(address nftContract, uint256 tokenId) public {
      uint256 len = nfts.length;
      for (uint256 i = 0; i < len; i++) {

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2021-05-visorfinance-findings/issues/16_
