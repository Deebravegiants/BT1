# [M] Incompatibility With Rebasing/Deflationary/Inflationary tokens

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-01-trader-joe
Published: 2022-01-25
Source: https://github.com/code-423n4/2022-01-trader-joe-findings/issues/18
Type: code-finding

## Details
# Handle

defsec


# Vulnerability details

## Impact

The TraderJOE protocol do not appear to support rebasing/deflationary/inflationary tokens whose balance changes during transfers or over time. The necessary checks include at least verifying the amount of tokens transferred to contracts before and after the actual transfer to infer any fees/interest.

## Proof of Concept

https://github.com/code-423n4/2022-01-trader-joe/blob/main/contracts/RocketJoeStaking.sol#L133

https://github.com/code-423n4/2022-01-trader-joe/blob/main/contracts/RocketJoeFactory.sol#L132


## Tools Used

Code Review

## Recommended Mitigation Steps

- Ensure that to check previous balance/after balance  equals to amount for any rebasing/inflation/deflation
- Add support in contracts for such tokens before accepting user-supplied tokens
- Consider supporting deflationary / rebasing / etc tokens by extra checking the balances before/after or strictly inform your users not to use such tokens if they don't want to lose them.
