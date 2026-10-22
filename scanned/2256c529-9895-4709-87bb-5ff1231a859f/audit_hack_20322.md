# [M] 5.2.3 Unaccounted collateral is mishandled intriggerDefault

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** pool-v2::LoanManager.sol#L
**Description:** The control flow oftriggerDefaultis partially determined by the value ofMapleLoanLike(loan_-
).collateral() == 0. The code later assumes there are 0 collateral tokens in the loan if this value is true, which
is incorrect in the case ofunaccountedcollateral tokens. In non-liquidating repossessions, this causes an overes-
timation of the number offundsAssettokens repossessed, leading to a revert in the_disburseLiquidationFunds
function. Anyone can trigger this revert by manually transferring 1 Wei ofcollateralAssetto the loan itself. In liq-
uidating repossessions, a similar issue causes the code to call the liquidator'ssetCollateralRemainingfunction
with only accounted collateral, meaning unaccounted collateral will be unused/stuck in the liquidator.
**Recommendation:** In both cases, use the collateral token'sbalanceOffunction to measure the amount of collat-
eral tokens in the loan, for example:

- if (IMapleLoanLike(loan_).collateral() == 0 || IMapleLoanLike(loan_).collateralAsset() == fundsAsset)
    ,! {
+ address collateralAsset_ = IMapleLoanLike(loan_).collateralAsset();
+ if (IERC20Like(collateralAsset_ ).balanceOf(loan_) == 0 || collateralAsset_== fundsAsset) {

**Maple:** Fixed in #211.
**Spearbit:** Fixed.
