# [M] Risk of Having Two Wawa NFT(Avatar) NFTs Being Assigned Iden- tical TokenURI

## Summary
Severity: Medium
Contest weight: 0.4145
Dataset id: 16390
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The SetTokenURI() function in WawaNFT.sol contract is used to assign a tokenURI to the Wawa NFT (Avatar) that is to be minted, upon calling the GetWawa.claimWawa() function which internally calls the WawaNFT.getWawa() function. Each Wawa NFT(Avatar) must have a unique tokenURI, but there is no check for passing an already-used tokenURI.
The impact is this break the initial promise of the protocol that each user will get a unique Wawa NFT (Avatar).
The following scenario can happen:
1. Alice wants to claim/mint a new unique Wawa NFT(Avatar).
2. Alice calls the GetWawa.claimWawa() function and she gets a new unique Wawa NFT(Avatar).
3. Bob, a malicious user sees the successful transaction of Alice and copies her tokenURI and then calls the GetWawa.claimWawa() function with Alice’s tokenURI.
4. Alice and Bob have one Wawa NFT(Avatar) token each with the same metadata.

## Recommendation
Implement a check if the tokenURI that will be assigned when calling the setTokenURI() function has already been used for the minting of another unique Wawa NFT(Avatar). We recommend the implementation of a mapping that will indicate if the tokenURI that is passed has been used before.
Example:
```solidity
mapping(string tokenURI => bool) public createdTokenURI;
Error TokenURIAlreadyUsed();

function setTokenURI(uint256 tokenId , string memory tokenURI) public virtual onlyOwner {
    if(createdTokenURI[tokenURI]) revert TokenURIAlreadyUsed();
    createdTokenURI[tokenURI] = true;
    allWawa[tokenId].tokenURI = tokenURI;
    emit SetTokenURI(tokenId , tokenURI);
}
```
