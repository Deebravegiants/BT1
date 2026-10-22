# [M] Proper ownerOf() Logic in VirtualDoNFT

## Summary
Severity: Medium
Contest weight: 0.4089
Dataset id: 11927
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Double is an NFT rental protocol that allows holders to earn passive income by renting out valuable NFTs with utilities. At the core of the protocol is the BaseDoNFT contract, which is inherited by other contracts such as WrapDoNFT, VirtualDoNFT, and DclDoNFT. While reviewing the VirtualDoNFT contract, we notice that the function ownerOf() needs to be improved.
To elaborate, we show below this ownerOf() function. As the name indicates, this function is designed to query the owner of the given NFT. It comes to our attention that when the given tokenId is a wrapped NFT, the query is redirected to the original token contract. However, it still uses the same tokenId (line 19) which only makes sense to itself. In other words, we need to use doNftMapping[tokenId].oid as the applicable tokenId!
```solidity
function ownerOf(uint256 tokenId) public view virtual override returns (address) {
    if (isWNft(tokenId)) {
        return ERC721(oNftAddress).ownerOf(tokenId);
    }
    return ERC721(address(this)).ownerOf(tokenId);
}
```

## Recommendation
Properly use the right tokenId to query its owner.
