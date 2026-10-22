# [M] `MarketFees`: Seller referrer fee can underflow

## Summary
Severity: Medium
Contest weight: 0.5871
Dataset id: 17040
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In `MarketFees._getFees`, the `sellerReferrerFee` is deducted from `creatorRev` or `sellerRev` (depending on if the sale is primary / secondary):

```solidity
if (sellerReferrerTakeRateInBasisPoints != 0) {
  sellerReferrerFee = (price * sellerReferrerTakeRateInBasisPoints) / BASIS_POINTS;

  // Subtract the seller referrer fee from the seller revenue so we do not double pay.
  if (sellerRev == 0) {
    // If the seller revenue is 0, this is a primary sale where all seller revenue is attributed to the "creator".
    creatorRev -= sellerReferrerFee;
  } else {
    sellerRev -= sellerReferrerFee;
  }
}
```

`sellerReferrerTakeRateInBasisPoints` can be up to 5,000 (50%), because the exhibition take rate (which is the only case when a non-zero value is passed) needs to be smaller than `MAX_TAKE_RATE`. On the other hand, it is only enforced that the protocol fee plus the creator royalty percentage is smaller than 100%:

```solidity
if (
  protocolFeeInBasisPoints < BASIS_POINTS / BUY_REFERRER_FEE_DENOMINATOR ||
  protocolFeeInBasisPoints + BASIS_POINTS / CREATOR_ROYALTY_DENOMINATOR >= BASIS_POINTS
) {
  /* If the protocol fee is invalid, revert:
   * Protocol fee must be greater than the buy referrer fee since referrer fees are deducted from the protocol fee.
   * The protocol fee must leave room for the creator royalties.
   */
  revert NFTMarketFees_Invalid_Protocol_Fee();
}
```

Because of that, there are valid settings where the calculation will underflow, leading to sales that do not succeed. For instance, we can have a protocol fee of 20% and creator royalties of 35%, in which case `sellerRev` would be 45% of the overall price. If the exhibition take rate is then >45%, the calculation will underflow.

## Recommendation
There are two options to solve the problem:

  * Enforce that the protocol fee plus the creator royalty percentage is less than 50%.
  * Handle the underflow case explicitly and for instance cap the seller referrer fee if it would exceed the seller revenue.

Also emit the event in `_getAndRemoveNftFromExhibition`
