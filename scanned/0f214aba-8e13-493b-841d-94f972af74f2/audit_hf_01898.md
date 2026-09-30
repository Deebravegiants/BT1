# [H] buyNFT does not check if a listing id was canceled

## Summary
Severity: High
Contest weight: 0.6105
Dataset id: 10478
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function buyNFT(
    uint256 _listId,
) external payable nonReentrant isListedNFT(_listId) {
    ListNFT storage listedNft = listNfts[_listId];
    // require(_tokenId > 10, "NFT is already sold through Raffle");
    require(
        "Invalid pay token"
    );
    require(!listedNft.sold, "NFT already sold");
    require(msg.value >= listedNft.price, "Invalid price");
    listedNft.sold = true;
    listedNft.status = Status.COMPLETED;
    uint256 totalPrice = msg.value;
    if (!nftSold[_nft][listedNft.tokenId]) {
        _processInitialSale(totalPrice);
        nftSold[_nft][listedNft.tokenId] = true;
    } else {
        totalPrice = _processResale(totalPrice);
        // payable(listedNft.seller).transfer(totalPrice);
        (bool sent, ) = payable(listedNft.seller).call{value:
            totalPrice}(
        );
        require(sent, "Ghost: Failed to transfer fee to fee to
        MidNight.");
    }
}
```
the function above allows a user to buy an nft that is listed, the problem occurs because the function never
does validate that the nft lisiting has been canceled or not.
For example let us say a user has listed an nft for 1 eth, the lister canceled the listing and relisted the nft for
10 eth because his first listing was either done a long time ago or was a mistake.
Although the lister has updated the price and canceled the previous listing id. A malicious user can still
buyNFT with the canceled listing id in order to buy the nft for the cheaper price of 1 eth instead of 10 eth
even if the lister has canceled the listing.

## Recommendation
buyNFT function should validate if the the listing was canceled.
