# [H] acceptOfferNFT can be frontrun to scam the seller

## Summary
Severity: High
Contest weight: 0.6171
Dataset id: 10468
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function acceptOfferNFT(
    uint256 _tokenId,
    uint256 _listingId
) external nonReentrant isOfferredNFT(_nft, _tokenId, _offerer) isListedNFT(_listingId) {
    require(listNfts[_listingId].seller == msg.sender, "Not listed owner");
    OfferNFT storage offer = offerNfts[_nft][_tokenId][_offerer];
    ListNFT storage list = listNfts[offer.listingId];
    require(!list.sold, "Already sold");
    require(!offer.accepted, "Offer already accepted");
    list.sold = true;
    list.status = Status.COMPLETED;
    offer.accepted = true;
    uint256 offerPrice = offer.offerPrice;
    if (!nftSold[_nft][_tokenId]) {
        _processInitialSale(offerPrice);
        nftSold[_nft][_tokenId] = true;
    } else {
        offerPrice = _processResale(offerPrice);
        payable(list.seller).transfer(offerPrice);
    }
}
```
The acceptOfferNFT function allows a seller to accept an offer from a user to sell their nft. The problem occurs because the code allows the offerer to front run this tx when he sees it in mempool. Let us say the owner sees an offer for 1 eth and then calls the function to accept the offer. The attacker can frontrun the tx with 2 transactions, one where he cancels the current offer, and the second tx he submits a new offer for a very low amount, 1 wei. The victim user's tx will now pass and will accept the 1 wei offer even when he was trying to accept the 1 ether offer. The user was essentially robbed of his nft. This is possible because the OfferNFT mapping is updated and can be frontrun to do this attack.

## Recommendation
Add mechanisms such as offer ids to ensure the frontrun attack cannot happen. For example, offer id 1 was accepted but offer id 2 was not. This means that if offer id 1 is canceled, the user is not forced to sell to offer id 2. Furthermore, the protocol may also add a param named minimumAmount which validates the user is receiving at least the minimumAmount desired.
