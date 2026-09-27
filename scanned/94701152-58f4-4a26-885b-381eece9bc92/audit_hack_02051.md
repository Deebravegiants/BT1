# [H] 6.1 Low Decimal Token Issues

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design High Version 3 Code Corrected


The lower the decimals of a token are and the higher the value, the more severe rounding issues will
become. Simultaneously, the liquidity position accounting with 18 decimals will cause issues.

Examples issues are:

Burning one unit of a low decimal but high value token (in create) might be a huge loss for the user.

There is a dependency between the delta when creating a pool and the decimals of a token. delta
cannot be chosen freely because of this dependency (1e18 - delta) - 1e(18-decimals) needs
to be bigger than 1 , else the create will revert. This basically eliminates the support of zero decimal
tokens (as the only viable option is delta = 0). Low decimals limit the range of delta and the step
accuracy with which the risky token amount is calculated. E.g. the maximum value of delta can be
9e17 (should be 1e18) for 1 decimals, 99e16 for 2 decimals and so on. The step size should be
accordingly high to increase the resulting delRisky one unit.

With decreasing decimals this calculation will lose precision if the token decimals are not dividable by the
fraction delLiquidity / PRECISION with modulo zero.

```
delRisky = (delRisky * delLiquidity) / PRECISION; // liquidity has 1e18 precision, delRisky has native precision
delStable = (delStable * delLiquidity) / PRECISION;
```
The function getAmounts has a similar problem and will losing precision. This can be exploited in
allocate to receive more liquidity tokens than the user would be entitled to as the rounding in
allocate is in the user's favor.

Code corrected

The issues above have been tackled by only accepting token decimals between six and 18. Six was
chosen to support famous stable coins and did not lead to issues in tests. However, tests and fuzzing
does not cover all possible states and due to the complex math, there might be a state that still results in
issues regarding to the decimals.
