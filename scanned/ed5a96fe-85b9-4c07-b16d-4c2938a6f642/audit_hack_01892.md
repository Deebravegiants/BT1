# [H] 6.2 Price Precision Very Low for Some Tokens

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness High Version 1 Code Corrected

Pairs containing a very low-value token and a low decimal token create some precision issues. Assume
the existence of a token named TOK with 18 decimals and another token named USD with 6 decimals
precision. Let's say the price of TOK is 0.00001 USD per TOK.

If a user wants to buy some TOK at constant price P = 0.00001 USD per TOK, then they need to
compute the B parameter this way:

```
B = 2^32 * sqrt(0.00001 * 1e6 / 1e18)
B = 13.
```
However, B must be an integer, meaning it will be rounded up or down (depending on the frontend
implementation). In any case, the price will differ greatly from the intended price resulting in possible loss
or no execution for the user.

Note: This issue was already disclosed by Bancor at the beginning of the audit.

Code corrected:

Bancor added precision by increasing the multiplying factor to 2^48 instead of 2^32, and implemented an
encoding logic to be able to stretch the range of possible rates. Values greater than 2^48 now can have a
(negligible) precision loss.
