# [C] Namada-apps allows Excessive Computation in Mempool Validation

## Summary
Severity: Critical
Advisory: GHSA-f8qm-hmm3-fv7f
CWE: CWE-770
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H (CVSS_V4)
Published: 2025-02-20
Source: https://github.com/advisories/GHSA-f8qm-hmm3-fv7f
Type: github-advisory

## Affected
- crates.io: `namada-apps` — affected >=1.0.0 <1.1.0

## Details
### Impact

A malicious transaction may cause an expensive computation in mempool validation.

A transaction with multiple repeated sections causes the section hash calculation used for signature validation to grow exponentially (and potentially even cubic) in proportion to number of sections. This may be used to significantly slow down operation of nodes.

### Patches

This issue has been patched in apps version 1.1.0. The transaction sections are now being checked for uniqueness and the number of permitted sections contained in a single transaction has been limited to 10,000.

### Workarounds

There are no workarounds and users are advised to upgrade.

## References
- https://github.com/anoma/namada/security/advisories/GHSA-f8qm-hmm3-fv7f
- https://github.com/anoma/namada
