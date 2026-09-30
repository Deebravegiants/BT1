# [M] SomeTrade-TerminatingFunctionsDoNotCall removeAssetIdUsed() Internally, Potentially Leading The Same Skin Not Being Tradable On CSX Again

## Summary
Severity: Medium
Contest weight: 0.4296
Dataset id: 7021
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Unlike other trade-terminating functions, CSXTrade::buyerCancel(), CSXTrade::sellerTradeVeridict() and CSXTrade::sellerConfirmsTrade() don’t call Users::removeAssetIdUsed() after transferring the committed tokens to the buyer/seller. And since asset IDs are the unique identifiers of Steam items, this means that the same skin won’t be tradable on CSX again. Although asset IDs change, they do so only when the items are traded or changed in some way, so it is unlikely that users will know how or want to change the asset ID of their skin, in order for it to become tradable on CSX again. This can prove to be especially problematic with the CSXTrade::buyerCancel() function, as it can be used to intentionally DoS the trading of concrete user skins.

Some skins will become impossible to trade on CSX for an undefined amount of time.

## Recommendation
Add a Users::removeAssetIdUsed call at the appropriate places in all the above-mentioned functions:
```solidity
function buyerCancel() external onlyAddress(buyer) nonReentrant {
    // code
    IUSERS_CONTRACT.changeUserInteractionStatus(address(this), buyer,
    status);
    _transferToken(address(this), buyer, depositedValue);
    + _rmvAId();
}

function sellerTradeVeridict(
    bool _sellerCommited
) external onlyAddress(SELLER_ADDRESS) nonReentrant {
    // code
} else {
    _changeStatus(TradeStatus.SellerCancelledAfterBuyerCommitted , "
    SE_DEFAULT");
    IUSERS_CONTRACT.changeUserInteractionStatus(address(this),
    SELLER_ADDRESS , status);
    IUSERS_CONTRACT.changeUserInteractionStatus(address(this), buyer,
    status);
    _transferToken(address(this), buyer, depositedValue);
    +
    _rmvAId();
}
}
function sellerConfirmsTrade() external onlyAddress(SELLER_ADDRESS)
nonReentrant {
    // code
    _changeStatus(TradeStatus.Completed , _data);
    IUSERS_CONTRACT.endDeliveryTimer(address(this), SELLER_ADDRESS);
    IUSERS_CONTRACT.changeUserInteractionStatus(address(this),
    SELLER_ADDRESS , status);
    IUSERS_CONTRACT.changeUserInteractionStatus(address(this), buyer,
    status);
    _distributeProceeds();
    + _rmvAId();
}
+ function _rmvAId() private {
+    bool _s = IUSERS_CONTRACT.removeAssetIdUsed(itemSellerAssetId ,
    SELLER_ADDRESS);
+    if (!_s) {
+        revert TradeIDNotRemoved();
+    }
+ }
```
