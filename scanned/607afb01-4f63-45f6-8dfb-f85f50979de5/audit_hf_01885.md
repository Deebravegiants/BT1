# [C] Direct theft of NFT through cancelListedNFT

## Summary
Severity: Critical
Contest weight: 0.2613
Dataset id: 10462
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A malicious user can directly steal any NFT in the marketplace because the _nft param is not correctly validated by the function. Let us take a look at the snippet...
```solidity
function cancelListedNFT(
    uint256 _listingId
) external nonReentrant isListedNFT(_listingId) {
    ListNFT memory listedNFT = listNfts[_listingId];
    require(listedNFT.seller == msg.sender, "not listed owner");
    IERC721(_nft).transferFrom(
        msg.sender,
        listedNFT.tokenId
    );
    // delete listNfts[_listingId];
    listNfts[_listingId].status = Status.CANCELLED;
}
```
the attacker can list a low-value nft of any token id, and then when they want to steal another NFT from a different collection but with the same token id, the attacker can simply call cancelListedNFT with a Because the logic does not check if the status of the listing id is already canceled, the attacker may drain every NFT of every collection in the contract with the same token id, he may then withdraw his NFT. Essentially an attacker can drain every NFT in the protocol if he just deposits the same token id and then

## Recommendation
user's NFT.
