# [M] `buyFromPrivateSaleFor

## Summary
Severity: Medium
Contest weight: 0.1241
Dataset id: 1602
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `buyFromPrivateSaleFor()` function allows sellers to make private sales to users. If insufficient `ETH` is provided to the function call, the protocol will attempt to withdraw the amount difference from the user’s unlocked balance. However, if the same user has an open offer on the same NFT, then these funds will remain locked until expiration. As a result, the user cannot make use of these locked funds even though they may be needed for a successful sale.

## Recommendation
Consider adding a `_cancelBuyersOffer()` call to the `buyFromPrivateSaleFor()` function. This should be added only to the case where insufficient `ETH` was provided to the trade. By cancelling the buyer’s offer on the same NFT, we can guarantee that the user has access to the correct amount of funds.
Yes - completely agree. This was an oversight on our end - and as a result it created an inconsistent experience for users. Since we leveraged an outstanding offer balance for a `buy` purchase, the same behavior should occur when using Private Sales so that user’s are not in a state where they cannot make the purchase due to incorrectly having their funds locked up.

As you point out without this change, it’s possible that the buyer using private sales continues to have their funds locked up for an Offer that can now only be accepted by themselves. It’s an awkward state that should be avoided.

We have made the recommended change.
