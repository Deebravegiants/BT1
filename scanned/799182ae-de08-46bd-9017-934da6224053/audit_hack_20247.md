# [H] 5.1.2 Old governor can callacceptGov()after renouncing its role through_abdicate()

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk

**Context:** Gov.sol#L

**Description** : The __abdicatefunction does not resetpendingGovvalue to 0. Therefore, if a pending governor is
set the user can become a governor by callingacceptGov.

**Recommendation:** Consider settingpendinGovtoaddress(0)inside the__abdicatefunction.

```
function __abdicate() governed external override {
address old = gov;
gov = address(0);
+ pendingGov = address(0);
emit NewGov(old, address(0));
}
```
