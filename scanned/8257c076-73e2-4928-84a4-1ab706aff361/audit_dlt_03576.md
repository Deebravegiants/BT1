# [M] M-07 Unmitigated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-angle-mitigation
Published: 2023-07-21
Source: https://github.com/code-423n4/2023-07-angle-mitigation-findings/issues/30
Type: code-finding

## Details
# Lines of code

https://github.com/AngleProtocol/angle-transmuter/blob/3e43e29d2b2f0b75876396e7c65e48c00c5fd1b2/contracts/transmuter/facets/Redeemer.sol#L119


# Vulnerability details

## Original Issue
https://github.com/code-423n4/2023-06-angle-findings/issues/8

## Details
This issue shows users may get fewer tokens than expected when the collateral list order changes.

As mitigation, it recommends checking the length of `minAmountsOut` and `ts.collateralList` as well as the token addresses to resolve the problem completely.

The original submission recommends like the below.

```
The problem could be alleviated a bit by checking the length of minAmountsOut (making sure it is not longer than ts.collateralList). 
However, that would not help if a collateral is revoked and a new one is added. 
Another solution would be to provide pairs of token addresses and amounts, which would solve the problem completely.
```

## Mitigation
PR: https://github.com/AngleProtocol/angle-transmuter/commit/f8d0bf7c4009586f7022d5929359041db3990175

It validates the length of `minAmountsOut` and `ts.collateralList` but doesn't compare the token addresses.

As a result, the original problem still exists when a collateral is revoked and a new one is added.

## Recommended Mitigation
We should check the token addresses of `minAmountsOut` and `ts.collateralList` to resolve the original issue completely.

## Conclusion
This issue wasn't mitigated properly.


## Assessed type

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-angle-mitigation-findings/issues/30_
