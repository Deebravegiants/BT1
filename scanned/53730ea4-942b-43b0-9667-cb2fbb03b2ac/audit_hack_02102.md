# [C] 6.2 CurvePriveProvider Uses the Spot Price

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security Critical Version 1 Code Corrected

The CurvePriceProvider smart contract uses the spot price of the curve pool to get the price of
assets. This is done by calling the get_dy() function on the curve pool.


Hence, an attacker could easily manipulate the price with a flash loan or a lot of liquidity. If this oracle is
used as a source of truth for a borrowing or liquidation mechanism, funds could be stolen from the
protocol.

Further note, that also the IPriceProvider's NatSpec is not accurate in that case as it specifies that
the TWAP is calculated.

Code removed:

All related code has been removed. Curve is not used as a price provider anymore.
