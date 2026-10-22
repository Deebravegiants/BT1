# [M] Null check in `pricePerShare`

## Summary
Severity: Medium
Contest weight: 0.0931
Dataset id: 1014
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
oracle can return `0` as a price of the share, in that case, 0 will be the denominator in some calculations which can cause reverts from SafeMath (for e.g here: [`WrappedIbbtc.sol` L148](https://github.com/code-423n4/2021-10-badgerdao/blob/main/contracts/WrappedIbbtc.sol#L148)) resulting in Denial Of Service.

  * [`WrappedIbbtcEth.sol` L73](https://github.com/code-423n4/2021-10-badgerdao/blob/main/contracts/WrappedIbbtcEth.sol#L73)
  * [`WrappedIbbtc.sol` L123](https://github.com/code-423n4/2021-10-badgerdao/blob/main/contracts/WrappedIbbtc.sol#L123)

## Recommendation
Add a null check to ensure that on every update, the price is greater than 0.

Agreed. we will implicitly or explicitly add this check.
