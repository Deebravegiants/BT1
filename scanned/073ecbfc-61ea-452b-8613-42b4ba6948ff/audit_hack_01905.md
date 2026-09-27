# [M] 5.1 execute() Gas Calculation Can Underflow

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 1 Risk Accepted

In AccountImplementation, execute() subtracts 5000 from gas() using assembly subtraction. If
gas() is less than 5000 , this will underflow and wrap around to a very high value.

The solidity overflow checks are disabled when using assembly, so this will not revert.

Risk accepted

Oasis accepts the risk of this underflow occurring and states that under normal use this will not happen,
as the proxy is intended for state-changing operations and hence the delegate call should never cost less
than 5000 gas to execute.
