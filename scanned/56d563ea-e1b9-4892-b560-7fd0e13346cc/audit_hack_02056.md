# [M] 6.8 Token Decimal Validation

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 3 Code Corrected

The engine contract supports tokens with different decimals. However, tokens with very few decimals and
more than 18 decimals cause severe issues but are allowed to be deployed by the factory.

Code corrected

The factory now validates decimals for both tokens before deploying an engine. Tokens with 6 to 18
decimals are supported.
