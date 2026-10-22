# [M] 6.1 Incorrect Computation of Product Term

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 1 Code Corrected

The product term pi in the whitepaper depends on D, w_i and x_i. The function _calc_vb_prod takes
as input _s which is the sum of tokens in the Pool and is different from D if the pool is not at equilibrium
point.

This issue was found by Yearn also while the review was ongoing.

Code corrected:

The function _update_weights has been updated to pass supply when calling function
_calc_vb_prod as follows:


```
supply: uint256 = self.supply
if supply > 0:
vb_prod = self._calc_vb_prod(supply)
```
Furthermore, the function _calc_vb_prod_sum, which is called on first deposit or when adding a new
asset, is revised to not take _s (sum term) as an input parameter.
