# [C] SA002

## Summary
Severity: Critical
Chain: Namada
Component: anoma/namada
Published: 2025-02-17
Source: https://github.com/namada-net/namada/security/advisories/GHSA-f8qm-hmm3-fv7f
Type: github-advisory

## Details
### Impact

A malicious transaction may cause an expensive computation in mempool validation.

A transaction with multiple repeated sections causes the section hash calculation used for signature validation to grow exponentially (and potentially even cubic) in proportion to number of sections. This may be used to significantly slow down operation of nodes.

### Patches

This issue has been patched in apps version 1.1.0. The transaction sections are now being checked for uniqueness and the number of permitted sections contained in a single transaction has been limited to 10,000.

### Workarounds

There are no workarounds and users are advised to upgrade.
