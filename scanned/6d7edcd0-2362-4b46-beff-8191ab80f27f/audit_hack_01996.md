# [M] 6.1 No Protection for Keepers

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Risk Accepted

Generally, keepers may just be interested in collecting the penalty of failing offers. In Mangrove however,
an offer could always succeed unexpectedly due to changing on-chain conditions. In this case, a
keeper/taker may have executed an offer he did not actually intended to take and which may had a bad
exchange rate. Note that offers may only fail when significant amounts of tokens are flashloaned to the
maker up front but the very same offer may succeed for lower amounts.

Unaware keepers may be tricked by honeypot offers (offers that appear to fail but in reality don't fail) by
malicious makers.

Keepers may protect themself by wrapping their call in a smart contract and checking for the expected
outcome, but the code of Mangrove itself does not offer such a feature directly.

Risk Accepted:

Giry responded: Indeed all keepers should wrap their calls in a reverting contract. This protective wrapper
does not need to be inside Mangrove. We plan to provide a standard wrapper at a separate address.
