# [M] 7.13 Governance Not Fully Propagated

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 1 Specification Changed

The documentation specifies the following:

```
The Core contract has the ability to add a new governor or remove a governor from the
system and propagate this change across all underlying contracts of the protocol.
```
Similarly, the Core contract should propagate guardian changes. However, that is not the case for some
contracts. For example, the changes are not propagated to OracleMulti or RewardsDistributor. That
mismatches the specification. Fortunately, the governance can use functions grantRole() and
revokeRole() to perform the changes jointly with the functions from Core.

Specification changed:

The documentation has been updated and now describes how the governance change propagates from
the Stablemaster. Additionally the code of the core contract now contains following comment:

```
Keeps track of all the StableMaster contracts and facilitates governance by allowing the propagation
of changes across most contracts of the protocol (does not include oracle contract,
RewardsDistributor, and some
```
