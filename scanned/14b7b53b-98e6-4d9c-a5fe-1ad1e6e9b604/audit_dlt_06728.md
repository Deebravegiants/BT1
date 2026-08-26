# [M] _onTransferReceived() does not work as intended

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-08-superposition
Published: 2024-09-16
Source: https://github.com/code-423n4/2024-08-superposition-findings/issues/148
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-08-superposition/blob/4528c9d2dbe1550d2660dac903a8246076044905/pkg/sol/OwnershipNFTs.sol#L92-L95


# Vulnerability details

## Impact
`_onTransferReceived` does not work as intended or described in the fucntion [natspec](https://github.com/code-423n4/2024-08-superposition/blob/4528c9d2dbe1550d2660dac903a8246076044905/pkg/sol/OwnershipNFTs.sol#L65-L67).
 - It will not revert when the recipient does not implement `onERC721Received()` function correctly (does not return `onERC721Received().selector`). 
- It will revert when the recipient implements `onERC721Received()` function correctly and as described/specified by the [EIP 712](https://eips.ethereum.org/EIPS/eip-721#specification) (returns `onERC721Received().selector`). 
- This will prevent transfers to contracts that have correctly implemented the `ERC721TokenReceiver` interface to accept safe token transfers via `safeTransferFrom()`.

## Proof of Concept
`_onTransferReceived()` has a require statement that will pass when the recipient does not return the `IERC721TokenReceiver.onERC721Received()` selector. [EIP 721](https://eips.ethereum.org/EIPS/eip-721#specification) defines that if a recipient is a contract, it should implement the `IERC721TokenReceiver.onERC721Received()` function and that function must return the `IERC721TokenReceiver.onERC721Received()` selector for it to be recognized as a valid erc721 token receiver. 

Snippet of the faulty require statement below 
https://github.com/code-423n4/2024-08-superposition/blob/4528c9d2dbe1550d2660dac903a8246076044905/pkg/sol/OwnershipNFTs.sol#L82-L95
```solidity
        bytes4 data = IERC721TokenReceiver(_to).onERC721Received(
            _sender,
            _from,
            _tokenId,

            // this is empty byte data that can be optionally passed to
            // the contract we're confirming is able to receive NFTs
            ""
        );

        require(
            data != IERC721TokenReceiver.onERC721Received.selector,
            "bad nft transfer received data"
        );
```
We can see that the require statement expects the data returned from the erc721 token receiver to **not be equal** to `IERC721TokenReceiver.onERC721Received.selector`. This means that if the recipient implements the `onERC721Received` function correctly and returns `IERC721TokenReceiver.onERC721Received.selector`, the require statement in function `_onTransferReceived()` will revert the whole transfer. 




_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-08-superposition-findings/issues/148_
