# [M] Users can lose their NFT

## Summary
Severity: Medium
Reporter: 0xweb3boy
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L61C1-L63C6
Type: audit-issue

## Details
# Users can lose their NFT

## Summary
Use safeMint instead of mint for ERC721

## Vulnerability Detail
_receiver will get the NFT whenever a user will call mint() function.
However, if msg.sender is a contract address that does not support ERC721, the NFT can be frozen in the contract.

As per the documentation of EIP-721:

A wallet/broker/auction application MUST implement the wallet interface if it will accept safe transfers.

## Impact

Users can possibly lose their NFTs

## Code Snippet
```solidity
 function mint(uint256 _tokenId, address _receiver) external onlyMinter { 
        _mint(_receiver, _tokenId);
    }
```

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L61C1-L63C6


## Tool used

Manual Review

## Recommendation
Use safeMint instead of mint to check received address support for ERC721 implementation.

https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC721/ERC721.sol#L262
