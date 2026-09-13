# [M] 6.3 No Sanity Checks for liquidationFactor

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

The liquidationFactor determines the liquidation penalty a user suffers based on the collateral
asset. When setting the liquidationFactor in the function _getPackedAsset, it should be checked
against the value of storeFrontPriceFactor. The storeFrontPriceFactor describes the
discount the protocol gives when someone buys liquidated collateral. If
liquidationFactor > storeFrontPriceFactor, then the protocol is expected to lose funds on
liquidations. Any user noticing this, could perform the following attack:

Sandwich significant price updates which decrease any of the collateral prices or increase the base asset
price using:

- Supply a collateral and borrow the maximum
- Absorb the account and liquidate

This would drain funds from the protocol. Hence, it should be ensured that this setting never exists.

Code corrected:

liquidationFactor is now assured to be smaller than or equal to storeFrontPriceFactor.
