# [M] 5.1.1 Freeze Redeems ifbondstoo Large

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** Bond.sol#L

**Description:** Issuing too many bonds can result in users being unable to redeem. This is caused by arithmetic
overflow inpreviewRedeemAtMaturity.

If a user’sbondsandpaidAmount’s (orbonds * nonPaidAmount) product is greater than2**256, it will overflow,
reverting all attempts to redeem bonds.

**Recommendation:** Implement a safety check in the factory as follows:

```
uint256 _safetyCheck_ = bonds * bonds;
```
Or inside the initialize function:

```
uint256 _safetyCheck_ = maxSupply * maxSupply;
```
Or changebondsin factory/Bond.initializeto a type ofuint128.

This ensures that bonds.mulDivDown(paidAmount, bondSupply) is always computable without overflow,
aspaidAmount is at mostmaxSupply(set duringinitialize) andbonds is at mostmaxSupply(set during
initialize).bonds * bondspassing the safety check ensures redeems remain functional.

**Porter:** Implemented in PR #290.

**Spearbit:** Acknowledged, recommendation has been implemented.
