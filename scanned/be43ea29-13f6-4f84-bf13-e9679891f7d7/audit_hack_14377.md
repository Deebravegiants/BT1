# [M] Not using safeMint can result in loss of NFT(s)

## Summary
Severity: Medium
Reporter: nican0r
Source: https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC721/ERC721.sol
Type: audit-issue

## Details
# Not using safeMint can result in loss of NFT(s)


## Summary
Using `_mint` instead of `_safeMint` can result in the loss of an NFT when minted to a contract address that doesn't fully implement the ERC721 specification for receiving contracts. 

## Vulnerability Detail
The [EIP-721 documentation](https://eips.ethereum.org/EIPS/eip-721) states that "a wallet/broker/auction application MUST implement the wallet interface if it will accept safe transfers". Therefore if a user mints a MeritNFT from a contract (multisig, etc.) that fails to implement this interface the NFT could become stuck in the contract because they are unable to transfer it out. 

The [OpenZeppelin ERC721 library](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC721/ERC721.sol) documentation also recommends the use of `_safeMint` over `_mint` to ensure the interface is properly implemented in the receiving contract before minting is completed:

```solidity
 /**
     * @dev Mints `tokenId` and transfers it to `to`.
     *
     * WARNING: Usage of this method is discouraged, use {_safeMint} whenever possible
     *
     * Requirements:
     *
     * - `tokenId` must not exist.
     * - `to` cannot be the zero address.
     *
     * Emits a {Transfer} event.
     */
    function _mint(address to, uint256 tokenId) internal virtual {
```

```solidity
/**
     * @dev Safely mints `tokenId` and transfers it to `to`.
     *
     * Requirements:
     *
     * - `tokenId` must not exist.
     * - If `to` refers to a smart contract, it must implement {IERC721Receiver-onERC721Received}, which is called upon a safe transfer.
     *
     * Emits a {Transfer} event.
     */
    function _safeMint(address to, uint256 tokenId) internal virtual {
```

## Impact
User could have an NFT stuck in the contract they minted with.

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/blob/ab734b575dc3b268de0457c2e3ab0e7d10cd7dd8/dutch-nft/src/MeritNFT.sol#L62C8-L62C8

## Tool used

Manual Review

## Recommendation
Implement the `_safeMint` function from OpenZeppelin in MeritNFT:

```solidity
  function mint(uint256 _tokenId, address _receiver) external onlyMinter {
        _safeMint(_receiver, _tokenId);
   }
```
