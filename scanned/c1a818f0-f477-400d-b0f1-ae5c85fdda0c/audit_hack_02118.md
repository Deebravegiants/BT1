# [M] 6.3 Critical Tests Missing

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

Some critical tests are missing in the test suite, for example, the e2e test for claiming a failed deposit is
incomplete.

Code corrected:

After Matter Labs provided the necessary sdk functions to generate the proof required by
claimFailedDeposit a test case was added.
