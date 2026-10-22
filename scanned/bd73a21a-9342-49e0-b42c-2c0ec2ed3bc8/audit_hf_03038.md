# [M] `MarketFees`: Primary sales not detected in some scenarios

## Summary
Severity: Medium
Contest weight: 0.5563
Dataset id: 17039
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When the seller is also a recipient of the creator royalties, a primary sale is assumed and `sellerRev` is set to 0:

```solidity
if (creatorRecipients[i] == seller) {
  // If the seller is any of the recipients defined, assume a primary sale
  creatorRev += sellerRev;
  sellerRev = 0;
}
```

However, this loop is exited prematurely when one of the `creatorShares` entries is greater than `BASIS_POINTS`:

```solidity
if (creatorShares[i] > BASIS_POINTS) {
  // If the numbers are >100% we ignore the fee recipients and pay just the first instead
  totalShares = 0;
  break;
}
```

Therefore, there can be scenarios where it is not detected that the seller is a recipient of the creator royalties and a secondary sale is assumed. For instance, if `creatorRecipients` is `[address(Bob), address(Alice), seller]` and `creatorShares` is `[100, 10_001, 100]`, the loop will `break` in the second iteration and `sellerRev` will not be set to 0.

## Recommendation
Continue looping to detect if the seller is a creator royalty recipient, even if one `creatorShares` entry was invalid.
