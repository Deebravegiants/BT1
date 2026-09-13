# [M] 7.2 Pricefeed of Oracle May Be Updated

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 1 Specification Changed

PriceOracle._addPriceFeed() is annotated with

```
/// @dev Sets price feed if it doesn't exist. If price feed is already set, it changes nothing
/// This logic is done to protect Gearbox from priceOracle attack
/// when potential attacker can get access to price oracle, change them to fraud ones
/// and then liquidate all funds
```
The function does not enforce this, a second call to this function allows to update the pricefeed for the
token.

Specification changed:

The description was erroneous and it was intended for the function to update the existing price feed. The
description was updated to reflect that.
