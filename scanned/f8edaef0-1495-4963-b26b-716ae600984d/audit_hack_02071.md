# [M] 7.14 Guardian Cannot Be Managed by Guardian

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 1 Code Corrected

The documentation specifies the following:

```
The guardian is indeed able to transfer its power to another address or to revoke itself.
```
However, that is not possible. Core functions setGuardian and revokeGuardian call the inherited
grantRole() and revokeRole(). The administrator of the guardian role is the governor role. Thus,
the calls grantRole() and revokeRole() would fail since the guardian is not allowed to access these
and the guardian cannot set or revoke guardians.

Code corrected:

Access control has been reimplemented. In the new implementation the guardian can transfer its power
to another address or revoke itself.
