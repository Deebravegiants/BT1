# [M] Rounding loss in and with approxPrice()

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-05-asymmetry-mitigation
Published: 2023-05-08
Source: https://github.com/code-423n4/2023-05-asymmetry-mitigation-findings/issues/71
Type: code-finding

## Details
# Rounding loss in and with approxPrice()

https://github.com/asymmetryfinance/smart-contracts/blob/ec582149ae9733eed6b11089cd92ca72ee5425d6/contracts/SafEth/SafEth.sol#L87-L119
https://github.com/asymmetryfinance/smart-contracts/blob/ec582149ae9733eed6b11089cd92ca72ee5425d6/contracts/SafEth/SafEth.sol#L359-L373

## Description
[`SafEth.approxPrice()`](https://github.com/asymmetryfinance/smart-contracts/blob/ec582149ae9733eed6b11089cd92ca72ee5425d6/contracts/SafEth/SafEth.sol#L359-L373) contains a rounding loss of the form `a/k + b/k <= (a + b)/k` which can be refactored as follows:
```diff
for (uint256 i = 0; i < count; i++) {
    if (!derivatives[i].enabled) continue;
    IDerivative derivative = derivatives[i].derivative;
    underlyingValue +=
-         (derivative.ethPerDerivative() * derivative.balance()) /
-         1e18;
+         (derivative.ethPerDerivative() * derivative.balance())
}
if (safEthTotalSupply == 0 || underlyingValue == 0) return 1e18;
- return (1e18 * underlyingValue) / safEthTotalSupply;
+ return underlyingValue / safEthTotalSupply;
```

But even with this refactoring, in `stake()` we have [the line](https://github.com/asymmetryfinance/smart-contracts/blob/ec582149ae9733eed6b11089cd92ca72ee5425d6/contracts/SafEth/SafEth.sol#L114)
`mintedAmount = (totalStakeValueEth * 1e18) / preDepositPrice;`
where `preDepositPrice = approxPrice()`, so this suffers a rounding loss of the form `a/(b/c) >= a*c/b`.
We would want to refactor this line to
`mintedAmount = (totalStakeValueEth * 1e18 * safEthTotalSupply) / underlyingValue;`.

We have another [case of `a/k + b/k <= (a + b)/k` in `stake()`](https://github.com/asymmetryfinance/smart-contracts/blob/ec582149ae9733eed6b11089cd92ca72ee5425d6/contracts/SafEth/SafEth.sol#L98-L112):
```solidity
for (uint256 i = 0; i < count; i++) {
    ...
    uint256 derivativeReceivedEthValue = (derivative
        .ethPerDerivative() * depositAmount) / 1e18;
    totalStakeValueEth += derivativeReceivedEthValue;
    ...
}
```
So we can do the same here and defer the division by `1e18` to after the summation, which gives us

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-05-asymmetry-mitigation-findings/issues/71_
