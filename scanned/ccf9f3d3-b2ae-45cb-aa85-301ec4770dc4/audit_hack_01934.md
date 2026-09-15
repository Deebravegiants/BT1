# [M] 6.4 Fee Approval Required

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security Medium Version 1 Code Corrected

Fees are charged by transferring the respective amount of tokens from the receiving user's account to
the fee receiver.

The user has to give additional approval for the token they actually want to receive, which is
counter-intuitive and also opens up additional security risks. Since the fee is always smaller than the
amount of tokens sent to the user, this special behavior is not necessary as the fees could also be
deducted from the amount sent to the user.

Code correct

Fees are deducted directly on the exchange, instead of being pulled from the order maker. Additionally,
_fillOrder implicitly collects fees by transferring the taking amount minus the fee from the operator.
