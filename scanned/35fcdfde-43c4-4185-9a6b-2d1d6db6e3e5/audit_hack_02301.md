# [M] \[M05\] Test coverage script fails to deliver the report

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Even though the project uses the [Brownie package](https://eth-brownie.readthedocs.io/en/stable/quickstart.html) to automate the tests and compile the contracts, running the script to get the coverage of the tests throughout the codebase ends up in a frozen task without ever delivering the actual code coverage report. Without this report it is impossible to know whether there are parts of the code never executed by the automated tests; so for every change, a full manual test suite has to be executed to make sure that nothing is broken or misbehaving.

Consider fixing and documenting how to run the test coverage scripts and making that coverage reach at least 95% of the source code.

_**Update:** Acknowledged. Notional’s statement for this issue:_

> _This is currently an issue with performance limitations in ganache and the way that brownie runs its tests. It’s on my list to dig into this in more depth and get it fixed but won’t be fixed as a result of this audit._
