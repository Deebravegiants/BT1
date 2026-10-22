# [M] 5.3.9 adminin theInsurancecontract can never be set

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** Insurance.sol#L41-L

**Description:** Theinitialize()function inInsurance.soldoes not setadmin. As such, it is impossible for the
adminto be set assetAdmin()can only be called by the contract's admin.

This makes it impossible for the admin to callcoverLoss()should the need arise.

**Recommendation:** Consider settingadminininitialize().
