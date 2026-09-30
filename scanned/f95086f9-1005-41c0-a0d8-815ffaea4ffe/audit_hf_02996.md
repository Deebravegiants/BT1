# [M] SafeAccessControlEnumerableCaller and SafeOwnableCaller contracts lack access control

## Summary
Severity: Medium
Contest weight: 0.1424
Dataset id: 16723
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The SafeAccessControlEnumerableCaller and SafeOwnableCaller contracts are abstract contracts that are used to call privileged functions in the SafeAccessControlEnumerable and SafeOwnable contracts. 

Contracts that inherit from *caller are required to override the non-view functions in the *caller contract to prevent anyone from calling privileged functions in *caller.

But once the inheriting contract does not override all the non-view functions, anyone can call the unoverridden privileged functions in the *caller.

Since the functions implemented in the abstract contract are no longer forced to be implemented again by the inheriting contract, the contract can be deployed even if the inheriting contract does not override all the non-view functions.

## Recommendation
Consider adding simple access control to the *caller contract. Or instead of implementing functions in the *caller, provide the code as comments or documentation for use in inheriting contracts.

prePO (sponsor) confirmed and resolved:
Fixed in [PR 352](https://github.com/prepo-io/prepo-monorepo/pull/352).

cccz (warden) reviewed mitigation:
Fixed by removing all write methods from `SafeOwnableCaller` `and SafeAccessControlEnumerableCaller` to ensure that the inheriting contracts need to override all write methods. This will avoid missing out of access control on some critical write methods.
