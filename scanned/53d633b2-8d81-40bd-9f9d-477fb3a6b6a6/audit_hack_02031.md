# [H] 6.1 Frozen Users Can Unfreeze Themselves

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design High Version 1 Code Corrected

A frozen user can call renounceRole from AccessControlUpgradeable and unfreeze themselves.
Note, that the Open Zeppelin implementation assumes that roles entail privileges and thus, any user can
give them up if they want to.

Moreover, the last admin could circumvent the check that enforces at least one admin for the contract by
calling renounceRole. However, this functionality will not be available in the front end so we do not
expect an admin to call renounceRole by mistake.

Code corrected:

renounceRole has been overriden by METL contract, also implementing check to prevent frozen users
to unfreeze themselves and last default admins renouncing themselves.
