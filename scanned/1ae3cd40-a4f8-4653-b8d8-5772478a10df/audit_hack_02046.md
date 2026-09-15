# [M] 6.5 FxPriceFeed setExchangeRate Timestamp

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

The exchange rate on FxPriceFeed is set by setExchangeRate function and recorded timestamp is
taken from the block. Since the transactions can be delayed and reordered or put to the chain earlier than
needed, the rate can be outdated by the time the block is mined. The recorded timestamp can give
unreliable information about the rate status. Some approaches, like Maker price oracles, ensure that new
price values propagated from the Oracles are not taken up by the system until a specified delay has
passed.


Code corrected:

Field pricingTime was added to the FxPriceFeed contract.
