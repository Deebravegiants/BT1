# [M] 5.3.4 USDConversionscan swap locked funds

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** USDConversions.sol#L71-L73, USDYieldManager.sol#L

**Description:** DAI tokens in the yield manager that are locked for finalized withdrawals can be swapped to other
USD yield tokens. User withdrawals can fail after finalization because of this.

**Recommendation:** Consider reverting if locked funds are swapped. It should be enough to check this in the
USDYieldManager.convertcall as other calls to_convertalways perform a transfer from the user before (the
USDConversionslibrary does not have access to the locked amount).
