# [H] 6.3 Fee Rate Not Hashed

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design High Version 1 Code Corrected

Hashing.hashOrder does not include the fee rate of an order into the hash. If the signatures are also
generated this way and users do not recognize this, operators can always specify MAX_FEE_RATE_BIPS
fees.

Code correct

Order hash computation now includes feeRateBps.
