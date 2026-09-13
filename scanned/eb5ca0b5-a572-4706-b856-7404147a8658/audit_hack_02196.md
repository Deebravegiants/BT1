# [M] fees can be any amount

## Summary
Severity: Medium
Source: https://github.com/code-423n4/2022-02-redacted-cartel/blob/main/contracts/BribeVault.sol#L256
Type: audit-issue

## Details
# Lines of code

https://github.com/code-423n4/2022-02-redacted-cartel/blob/main/contracts/BribeVault.sol#L256


# Vulnerability details

in `transferBribes`, the fees are user input, rather than  calculation using `fee` (state var).
currently, `fee` is unused:
https://github.com/code-423n4/2022-02-redacted-cartel/blob/main/contracts/BribeVault.sol#L23

therefore the fees amounts might be wrong.
