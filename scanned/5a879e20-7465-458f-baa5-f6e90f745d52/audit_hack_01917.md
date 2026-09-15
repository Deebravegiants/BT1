# [H] 6.1 Possible Frontrunning on Registration

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design High Version 1 Code Corrected

If a delegatee already deployed its DelegatedShare contact on its own and want to register it with
register(IDelegatedShare shareToken, address defaultFarm), another user could front
run the transaction and register the already deployed contract in place of the true delegatee, who won't
be able to register the contract for itself.

This can become problematic if the DelegatedShare contract already has some accounting done.

Code corrected:

The register(IDelegatedShare shareToken, address defaultFarm) function has been
removed.
