# [M] Loss of precision in divisions

## Summary
Severity: Medium
Reporter: Joyful Macaroon Shrimp
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
# Loss of precision in divisions
### <a name="L-3"></a>[L-3] Loss of precision in divisions

#### Impact:
Division by large numbers may result in the result being zero, due to Solidity not supporting fractions. Consider requiring a minimum amount for the numerator to ensure that it is always larger than the denominator.

*Instances (1)*:
```solidity
File: LiqBorrowingMan/LiquidityBorrowingManager.sol

971:         uint256 platformFees = (fees * platformFeesBP) / Constants.BP;

```
