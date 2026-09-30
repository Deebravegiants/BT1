# [M] FeeBuyback.submit doesn't allow to pay fee in eth

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-telcoin
Published: 2022-11-22
Source: https://github.com/sherlock-audit/2022-11-telcoin-judging/issues/3
Type: sherlock-finding

## Details
rvierdiiev

medium

# FeeBuyback.submit doesn't allow to pay fee in eth

## Summary
FeeBuyback.submit doesn't allow to pay fee in eth only.
## Vulnerability Detail
Because of [check](https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L55-L57) that token is not 0 it's not possible to pay fee in native token. However it's possible that user will want to exchange only native token to TEL.
## Impact
Can't pay fee with native token only.
## Code Snippet
https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L55-L57
## Tool used

Manual Review

## Recommendation
Add ability to provide some specific token address that explains that only native token is used for swap.
