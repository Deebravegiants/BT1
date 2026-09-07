# [C] SA001

## Summary
Severity: Critical
Chain: Namada
Component: anoma/namada
Published: 2025-02-17
Source: https://github.com/namada-net/namada/security/advisories/GHSA-82vg-5v4f-f9wq
Type: github-advisory

## Details
### Impact

A malicious transaction may cause a crash in mempool validation.

A transaction with authorization section containing 256 public keys or more with valid matching signatures triggers an integer overflow in signature verification that causes a the node to panic.

### Patches

This issue has been patched in apps version 1.1.0. The mempool validation has been fixed to avoid overflow.

### Workarounds

There are no workarounds and users are advised to upgrade.
