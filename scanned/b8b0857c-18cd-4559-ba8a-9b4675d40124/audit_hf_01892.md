# [H] Making more than 1 offer on an item will cause loss of eth

## Summary
Severity: High
Contest weight: 0.7865
Dataset id: 10469
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function offerNFT(
    uint256 _listId,
) external payable isListedNFT(_listId) nonReentrant {
    require(msg.value > 0, "price can not 0");
    // require(_tokenId > 10, "NFT is already sold through Raffle");
    ListNFT memory nft = listNfts[_listId];
    offerNfts[_nft][nft.tokenId][msg.sender] = OfferNFT({
        nft: nft.nft,
        tokenId: nft.tokenId,
        offerer: msg.sender,
        payToken: _payToken,
        offerPrice: msg.value,
        accepted: false,
        listingId: _listId
    });
}
```
the offerNFT function allows a user to make an offer on an nft. The function is payable and the user must send eth via msg.value in order to make the offer. The problem occurs because the function does not correctly handle the case where the user plans to make more than 1 offer on the nft as is allowed on all marketplaces. for example let us say the user puts a 1 eth offer, he sends over 1 eth in msg value and the mapping is updated offerNfts[_nft][nft.tokenId][msg.sender] = OfferNFT({ the user wants to place another offer because his previous offer was to low, this time he sends 2 eth, the mapping is overriden with the new data. offerNfts[_nft][nft.tokenId][msg.sender] = OfferNFT({ the previous data is lost so there is no way for the user to withdraw his previous deposit of 1 eth only the 2 eth.
```solidity
function cancelOfferNFT(
    uint256 _tokenId
) external nonReentrant isOfferredNFT(_nft, _tokenId, msg.sender) {
    OfferNFT memory offer = offerNfts[_nft][_tokenId][msg.sender];
    require(offer.offerer == msg.sender, "not offerer");
    require(!offer.accepted, "offer already accepted");
    delete offerNfts[_nft][_tokenId][msg.sender];
    payable(offer.offerer).transfer(offer.offerPrice);
    emit CanceledOfferredNFT(
        offer.nft,
        offer.tokenId,
        offer.payToken,
        offer.offerPrice,
        msg.sender
    );
}
```
above we can see the function will transfer the funds back according to the current mapping, the overridden data will not be able to retrieve the user 1 eth and is now lost forever.

## Recommendation
Either implement logic that will block making an offer if an offer on the item is currently active or add logic to handle multiple offers.
