# [M] \[M01\] Fee-less loans

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
The [calculateLoanOriginationFee function](https://gitlab.com/aave-tech/dlp/contracts/blob/1f8e5e65a99a887a5a13ad9af6486ebf93f57d02/contracts/fees/FeeProvider.sol#L27) of the `FeeProvider` contract is in charge of calculating the origination fee for a loan of the specified amount. To do so, it [multiplies the given amount by the originationFeePercentage](https://gitlab.com/aave-tech/dlp/contracts/blob/1f8e5e65a99a887a5a13ad9af6486ebf93f57d02/contracts/fees/FeeProvider.sol#L28) – a hardcoded value [set during construction to 0.0025 \* 1e18](https://gitlab.com/aave-tech/dlp/contracts/blob/1f8e5e65a99a887a5a13ad9af6486ebf93f57d02/contracts/fees/FeeProvider.sol#L20).

Due to how the [wadMul](https://gitlab.com/aave-tech/dlp/contracts/blob/1f8e5e65a99a887a5a13ad9af6486ebf93f57d02/contracts/libraries/WadRayMath.sol#L38) multiplication works in this particular case, `calculateLoanOriginationFee` can return 0 for amounts greater than 0\. Such unexpected behavior would allow for a user to take loans that would not pay an origination fee. In particular, all loans with an amount lower than 200 will be granted without accounting for a fee (see this simple [mathematical proof](https://www.wolframalpha.com/input/?i=Quotient%5B%28+%281e18+%2F+2%29+%2B+x+%2A+%280.0025e18%29+%29%2C+1e18%5D+%3D+0+%2C+x+%3E+0) for validation).

Should loans be expected to always charge a fee, consider implementing the necessary validations in `calculateLoanOriginationFee` so that the transaction reverts in case the calculated fee is zero. Otherwise, consider clearly documenting this behavior to prevent unexpected outcomes. Either way, it is highly advisable to implement thorough unit tests related to this feature, as no unit tests were found for the `calculateLoanOriginationFee` function.

**Update**: _Fixed in [MR#75](https://gitlab.com/aave-tech/dlp/contracts/merge%5Frequests/75/diffs). Now all loans that would not pay a fee are rejected._
