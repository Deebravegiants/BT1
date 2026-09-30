# [M] Strengthen oﬀerPricingType/TakingOﬀerType Validation in DotcV2

## Summary
Severity: Medium
Contest weight: 0.4281
Dataset id: 11924
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
To facilitate the trader offer management, Swam Open dOTC has defined a number of types and data structures. While examining two specific types, i.e., offerPricingType and TakingOfferType, we notice their enforcement in trade execution can be strengthened.
In the following, we shows the code snippet from the related takeOfferFixed() routine. This routine is used to take a fixed price offer. However, current logic does not validate the given offer (from the input offerId) is compliant with the indicated offer pricing type, i.e., OfferPricingType.FixedPricing. Moreover, current offer also has the so-called TakingOfferType that indicates whether the taker is allowed to take the full amount of assets or not. However, this TakingOfferType type is not enforced. The same issue is also applicable to the takeOfferDynamic() routine.
```solidity
function takeOfferFixed(uint256 offerId, uint256 withdrawalAmountPaid, address affiliate) external {
    DotcOffer memory offer = allOffers[offerId];
    offer.checkDotcOfferParams();
    offer.offer.checkOfferParams();
    if (withdrawalAmountPaid == 0 || withdrawalAmountPaid > offer.withdrawalAsset.amount) {
        withdrawalAmountPaid = offer.withdrawalAsset.amount;
    }
    offer.withdrawalAsset.checkAssetOwner(msg.sender, withdrawalAmountPaid);
    uint256 withdrawalAssetAmount = withdrawalAmountPaid;
}
```

## Recommendation
Improve the above-mentioned routines to honor the defined types, i.e., offerPricingType and TakingOfferType.
