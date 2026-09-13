# [M] Incompatibility With Rebasing/Deflationary/Inflationary token

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-03-biconomy
Published: 2022-03-16
Source: https://github.com/code-423n4/2022-03-biconomy-findings/issues/91
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-03-biconomy/blob/main/contracts/hyphen/token/TokenManager.sol


# Vulnerability details

## Impact
The scope contracts do not appear to support rebasing/deflationary/inflationary tokens whose balance changes during transfers or over time. The necessary checks include at least verifying the amount of tokens transferred to contracts before and after the actual transfer to infer any fees/interest.

## Proof of Concept
https://github.com/code-423n4/2022-03-biconomy/blob/main/contracts/hyphen/token/TokenManager.sol

## Tools Used

## Recommended Mitigation Steps
Make sure token vault accounts for any rebasing/inflation/deflation
Add support in contracts for such tokens before accepting user-supplied tokens
