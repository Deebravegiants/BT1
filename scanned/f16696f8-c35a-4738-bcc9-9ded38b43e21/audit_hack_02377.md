# [M] \[M05\] Lack of input validation

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Several functions in the Augur code base lack explicit checks of user-controlled parameters. While this practice is often used as a way to reduce gas costs, under no circumstances should the lack of input validation undermine security nor functionality. Some examples of issues of varying severity that steam from unsanitized input are **“\[C01\] All CASH tokens approved to Augur can be emptied”**, **“\[L04\] Externally-owned accounts can be registered as contracts in the Augur contract”** or even **“\[M08\] Factories may unexpectedly fail to create proxies”**.

Consider implementing [require statements](https://solidity.readthedocs.io/en/v0.5.4/control-structures.html?#error-handling-assert-require-revert-and-exceptions) where appropriate to validate all user-controlled input. Including clear user-friendly error messages (as reported in **“\[M02\] Missing error messages in require statements”**) is highly recommended as well.

**_Update_**_: input validation has been implemented across a_ [_series of commits_](https://github.com/AugurProject/augur/pull/2603/commits)_._
