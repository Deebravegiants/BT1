# [C] 6.1 Outdated Interfaces

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Critical Version 1 Code Corrected

The zkSync interfaces for L2Log and L2Message have been updated and the ones used in the DAI
bridge current codebase are deprecated. The malformed L2 logs or messages would block any attempt
of withdrawal or claim of a failed deposit.

Code corrected:

The structs used correspond now to the most recent version of the zkSync 2.0 structs.
