# [M] \[M03\] Missing test coverage report

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
There is no automated test coverage report. Without this report it is impossible to know whether there are parts of the code never executed by the automated tests; so for every change, a full manual test suite has to be executed to make sure that nothing is broken or misbehaving.

Consider adding the test coverage report and making it reach at least 95% of the source code.

_**Update**: Acknowledged. The EmptySetSquad team statement for this issue:_

> _Won’t currently fix – Solidity coverage tool currently incompatible with our setup._
