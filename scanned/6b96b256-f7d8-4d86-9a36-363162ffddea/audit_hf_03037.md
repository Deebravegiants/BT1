# [M] `MarketFees`: Seller referrer fee not paid when no creator royalty recipients exist for a sale

## Summary
Severity: Medium
Contest weight: 0.3857
Dataset id: 17038
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The logic to calculate the seller referrer fee is within the following `if` block:

```solidity
if (creatorRecipients.length != 0 || assumePrimarySale) {
  ...
}
```

When `creatorRecipients.length == 0` and `assumePrimarySale == false` (which is the case for `ExhibitionMarketMock`), the returned `sellerReferrerFee` will always be zero, no matter which value is passed for `sellerReferrerTakeRateInBasisPoints`. Therefore, the exhibition curator will not get the configured fee in such a scenario, although the seller referral fee should not depend on the existence of creator royalty recipients.

## Recommendation
Calculate the seller referrer fee also when no creator royalty recipients are defined (like it is done for the buyer referrer fee).
