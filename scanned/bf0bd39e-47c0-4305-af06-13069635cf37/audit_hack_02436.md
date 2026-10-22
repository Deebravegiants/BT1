# [M] Incorrect calculations

## Summary
Severity: Medium
Source: https://github.com/pods-finance/yield-contracts/blob/9389ab46e9ecdd1ea1fd7228c9d9c6821c00f057/contracts/vaults/BaseVault.sol#L196-L201
Type: audit-issue

## Details
We found the following instances of incorrect calculations in `view` functions that are not currently called internally:

* In the [previewWithdraw](https://github.com/pods-finance/yield-contracts/blob/9389ab46e9ecdd1ea1fd7228c9d9c6821c00f057/contracts/vaults/BaseVault.sol#L196-L201) function, the [DENOMINATOR over invertedFee](https://github.com/pods-finance/yield-contracts/blob/9389ab46e9ecdd1ea1fd7228c9d9c6821c00f057/contracts/vaults/BaseVault.sol#L199) is always bigger than 1 when the fee is non-zero. Hence, the final returned shares are always an overestimate. Further, the `withdrawFeeRatio` is multiplied to `shares` instead of `assets` as in other instances such as [\_getFee](https://github.com/pods-finance/yield-contracts/blob/9389ab46e9ecdd1ea1fd7228c9d9c6821c00f057/contracts/vaults/BaseVault.sol#L399-L403). Consider correcting the withdrawal fee calculation.
* The calculation in the [assetsOf](https://github.com/pods-finance/yield-contracts/blob/9389ab46e9ecdd1ea1fd7228c9d9c6821c00f057/contracts/vaults/BaseVault.sol#L277) function over-estimates the actual commitment by an additional `committedAssets`. Consider removing the extra component.

**Update:** _Partially fixed in commit `6d37029` in [PR#75](https://github.com/pods-finance/yield-contracts/pull/75). `previewWithdraw` does not include fees as stated in the [EIP](https://eips.ethereum.org/EIPS/eip-4626)._
