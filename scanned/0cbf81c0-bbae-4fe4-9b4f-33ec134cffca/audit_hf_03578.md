# [M] TRH-1 | Stored Custodian Becomes Invalid Upon Migration

## Summary
Severity: Medium
Contest weight: 0.0637
Dataset id: 19557
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Custodian is kept as a separate, immutable variable inside of the TokenRewardHooks instead of _asset.custodian being used. Upon Custodian migration through the CustodianMigrator, the address of the Custodian will change and TokenRewardHooks will continue to reference the old Custodian. This necessitates a TokenRewardHooks re-deploy as _custodian cannot be reset.

## Recommendation
Consider using the Custodian directly on the _asset instead of setting _custodian.
