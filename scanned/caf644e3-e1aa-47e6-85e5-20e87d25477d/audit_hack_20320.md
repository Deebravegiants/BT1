# [M] 7.2.2 Consider preventingCoverageFundAddressto be set asaddress(0).

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:**

- River.1.sol#L
- CoverageFundAddress.sol#L
**Description:** In the current implementation ofRiver.setCoverageFundandCoverageFundAddress.setboth func-
tion do not revert when the_newCoverageFundaddress parameter is equal toaddress(0).
If the Coverage Fund address is empty, theRiver._pullCoverageFundsfunction will return earlier and will not pull
any coverage fund.
**Recommendation:** If having an empty coverage fund address equal toaddress(0)is the intended behavior, we
suggest explaining in both the documentation and natspec comments the reason and document in which scenario
this could happen.
Otherwise, add inside theCoverageFundAddress.setfunction a sanity check on the new address and revert in
case of_newValue == address(0).
**Alluvial:** Added sanity check inside theCoverageFundAddress.setfunction in PR 169.
**Spearbit:** Acknowledged.
