# [?] Fixes possible deadlock upon epoch close (#719)

## Summary
Severity: Unknown
Chain: Centrifuge
Component: centrifuge/centrifuge-chain
Published: 2022-03-29
Source: https://github.com/centrifuge/centrifuge-chain/commit/6c596864a8bfc230bc92932b1d0bb56555162d5a
Type: security-commit

## Details
Fixes possible deadlock upon epoch close (#719)

* pools logic for deadlock solution

* Fix tests

* Tests

* prepare dev runtime

* Fix loan tests

* Reverting deadlock logic approch with MinSubmissionTime

* allow equal solutions to be sumitted

* Adapt tests to same solutions allowed

* Test for zero submission
