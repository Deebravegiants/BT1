# [M] \[M03\] Lack of event emissions

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
The codebase is completely devoid of event definitions or emissions. This makes it very difficult for users or other interested parties to track important changes that take place in the system.

Consider emitting events after sensitive changes take place to facilitate tracking and notify off-chain clients that may be following the contracts’ activity.

**Update**: _Partially fixed in [PR#21](https://github.com/BarnBridge/BarnBridge-SmartYieldBonds/pull/21). Several critical system functions do now emit events, but there are still contracts that lack event emissions. For example, no events are emitted by sensitive functions in the `Governed` contract. The referenced PR is based on commits that include other changes to the codebase which have not been reviewed by OpenZeppelin._
