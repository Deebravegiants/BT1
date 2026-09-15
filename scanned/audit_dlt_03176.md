# [M] Mitigation of M-01: Issue NOT fully mitigated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-05-asymmetry-mitigation
Published: 2023-05-08
Source: https://github.com/code-423n4/2023-05-asymmetry-mitigation-findings/issues/59
Type: code-finding

## Details
https://github.com/asymmetryfinance/smart-contracts/blob/ec582149ae9733eed6b11089cd92ca72ee5425d6/contracts/SafEth/SafEth.sol#L87-L119

## Mitigated issue
[M-01: Division before multiplication truncate minOut and incurs heavy precision loss and result in insufficient slippage protection](https://github.com/code-423n4/2023-03-asymmetry-findings/issues/1078)

The issue was a loss of precision of three different kinds.
(1) `(a/b)*c <= a*c/b` in the slippage calculations in `Reth.withdraw()`, `Reth.deposit()` and `SfrxEth.withdraw()`.
(2) `a/k + b/k <= (a + b)/k` in the calculations of `underlyingValue`, `totalStakeValueEth` in `SafEth.stake()`.
(3) `a/(b/c) >= a*c/b` in the calculation of `mintAmount` in `SafEth.stake()`.

## Mitigation review
The instances of (1) in `Reth.withdraw()` and `SfrxEth.withdraw()` have been correctly refactored.
But `Reth.deposit()` is now: 
```solidity
uint256 rethPerEth = (1e36) / ethPerDerivative();
uint256 minOut = ((rethPerEth * msg.value) * (1e18 - maxSlippage)) / 1e36;
uint256 idealOut = (rethPerEth * msg.value) / 1e18;
```
`minOut` is still of the form `(a/b)*c`. It should be refactored to
```solidity
uint256 minOut = (msg.value * (1e18 - maxSlippage)) / ethPerDerivative();
```
`idealOut` may then be refactored to
```solidity
uint256 idealOut = (1e18 * msg.value) / ethPerDerivative();
```
(which has the same precision.)

All of (2) and (3) remain unaltered however. [This duplicate of M-01](https://github.com/code-423n4/2023-03-asymmetry-findings/issues/1044) provides an explicit refactoring of `stake()` which solves them. However, because of the introduction of [`SafEth.approxPrice()`](https://github.com/asymmetryfinance/smart-contracts/blob/ec582149ae9733eed6b11089cd92ca72ee5425d6/contracts/SafEth/SafEth.sol#L359-L373) this refactoring will have to be reworked. Technically, this is an entirely new issue, which is why this is reported in detail in "Rounding loss in and with approxPrice()".
