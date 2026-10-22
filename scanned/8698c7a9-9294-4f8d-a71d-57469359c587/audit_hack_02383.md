# [C] \[C02\] Borrowers can avoid liquidation

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
When a loan is liquidated, the [reduction in the remaining principal](https://gitlab.com/aave-tech/dlp/contracts/blob/1f8e5e65a99a887a5a13ad9af6486ebf93f57d02/contracts/lendingpool/LendingPoolLiquidationManager.sol#L152) and the corresponding reduction in the total borrows (either [fixed](https://gitlab.com/aave-tech/dlp/contracts/blob/1f8e5e65a99a887a5a13ad9af6486ebf93f57d02/contracts/lendingpool/LendingPoolLiquidationManager.sol#L144) or [variable](https://gitlab.com/aave-tech/dlp/contracts/blob/1f8e5e65a99a887a5a13ad9af6486ebf93f57d02/contracts/lendingpool/LendingPoolLiquidationManager.sol#L146)) is calculated by subtracting the accrued interest from the amount to be repaid.

Conceptually, this is a combination of two separate operations: the accrued interest is added to the principal when constructing the new loan and then the amount repaid is subtracted. However, combining them into a single operation will cause the transaction to revert whenever the repayment is less than the accrued interest.

In addition to preventing valid repayments, this behavior could be exploited by borrowers to prevent liquidation.

Since the size of each liquidation transaction is [restricted by the amount of collateral that can be recovered](https://gitlab.com/aave-tech/dlp/contracts/blob/1f8e5e65a99a887a5a13ad9af6486ebf93f57d02/contracts/lendingpool/LendingPoolLiquidationManager.sol#L119-125) from the specified reserve, a borrower could spread their collateral across many different assets in order to ensure the maximum liquidation amount is lower than their accrued interest.

Alternatively, the liquidation amount is also [restricted by the protocol’s close factor](https://gitlab.com/aave-tech/dlp/contracts/blob/1f8e5e65a99a887a5a13ad9af6486ebf93f57d02/contracts/lendingpool/LendingPoolLiquidationManager.sol#L108), which means a user could simply allow their loan to grow until the interest exceeds this threshold. In practice, this will likely take years to occur.

In either case, when a borrower cannot be liquidated they no longer have any incentive to remain collateralized.

Consider updating the principal and total borrows variables in two independent steps that account for the accrued interest and the loan repayment respectively.

**Update**: _Fixed in [MR#56](https://gitlab.com/aave-tech/dlp/contracts/merge%5Frequests/56/diffs) and [MR#58](https://gitlab.com/aave-tech/dlp/contracts/merge%5Frequests/58/diffs). The principal and total borrows are updated in two steps._
