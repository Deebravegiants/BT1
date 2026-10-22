# [H] Lack of Input Validation in ChronosMarketplace::makeOfferWithETH()

## Summary
Severity: High
Contest weight: 0.6247
Dataset id: 11821
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned in Section 3.3, the ChronosMarketplace contract supports the Limit Order trading mode. In particular, one entry routine, makeOfferWithETH(), allows for submitting a limit order to buy the given NFT with ETH. While examining its logic, we observe its current implementation needs to be improved.

To elaborate, we show below the related code snippet of the contract. The makeOfferWithETH() routine allows the user to provide an arbitrary _paymentToken (e.g., WBTC) without any validation. With that, a malicious actor can steal the WBTC from the ChronosMarketplace contract via cancelOffer() even though he will lose the same amount of ETH.
```solidity
function makeOfferWithETH(
    address _nft,
    uint256 _tokenId,
    address _paymentToken,
    uint256 _offerPrice
) external payable override nonReentrant whenNotPaused {
    require(isChronosNft(_nft), Errors.NOT_CHRONOS_NFT);
    require(
        msg.value >= _offerPrice && _offerPrice > 0,
        Errors.INVALID_PRICE
    );
    address offeror = msg.sender;
    _setOfferId(offerId, offeror, true);
    offerInfos[offerId++] = OfferInfo(
        offeror,
        _paymentToken,
        _nft,
        _tokenId,
        _offerPrice
    );
}

function cancelOffer(uint256 _offerId) external override nonReentrant whenNotPaused {
    OfferInfo memory offerInfo = offerInfos[_offerId];
    address sender = msg.sender;
    require(sender == offerInfo.offeror, Errors.NOT_OFFEROR);
    delete offerInfos[_offerId];
    _setOfferId(_offerId, sender, false);
    if (offerInfo.paymentToken == address(0)) {
        payable(sender).transfer(offerInfo.offerPrice);
    } else {
        IERC20(offerInfo.paymentToken).safeTransfer(
            sender,
            offerInfo.offerPrice
        );
    }
    emit CancelOffer(_offerId);
}
```

## Recommendation
Validate the input _paymentToken parameter in the makeOfferWithETH() routine.
