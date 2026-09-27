# [H] 6.1 Wrong Computation of Borrow Balance

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness High Version 1 Code Corrected

The function borrowBalanceOf inside the CometExt uses baseSupplyIndex instead of
baseBorrowIndex to compute the borrow balance:

```
function borrowBalanceOf(address account) external view returns (uint256) {
int104 principal = userBasic[account].principal;
return principal < 0? presentValueBorrow(baseSupplyIndex, unsigned104(-principal)) : 0;
```
As a consequence, the result is incorrect.

Code corrected:

The borrowBalanceOf function now uses the correct index (i.e., baseBorrowIndex). In addition, unit
tests were updated to catch this issue by using a different value for baseSupplyIndex and
baseBorrowIndex.
