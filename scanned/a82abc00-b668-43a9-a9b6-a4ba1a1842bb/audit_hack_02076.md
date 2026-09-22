# [M] 6.6 Undeployable SmartNFTs

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 1 Code Corrected

SmartNFTs are used for the promissory note and obligation receipt. This contract inherits from
OpenZeppelin's access control contract. The deployment of the contract may fail.

```
_setupRole(DEFAULT_ADMIN_ROLE, _admin);
grantRole(LOAN_COORDINATOR_ROLE, _loanCoordinator);
```
It sets _admin as the default administrator for all roles. If _admin is not msg.sender, then grantRole
will fail.

Code corrected:

_setupRole() is now used instead of grantRole in the constructor.
