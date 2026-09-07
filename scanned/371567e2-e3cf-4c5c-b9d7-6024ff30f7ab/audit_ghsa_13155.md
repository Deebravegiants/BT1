# [M] Inventory exposes reference to non-Sync data to an arbitrary thread

## Summary
Severity: Medium
Advisory: GHSA-36xm-35qq-795w
Ecosystem: crates.io
Published: 2023-09-11
Source: https://github.com/advisories/GHSA-36xm-35qq-795w
Type: github-advisory

## Affected
- crates.io: `inventory` — affected >=0 <0.2.0

## Details
Affected versions do not enforce a `Sync` bound on the type of caller-provided value held in the plugin registry. References to these values are made accessible to arbitrary threads other than the one that constructed them.

A caller could use this flaw to submit thread-unsafe data into inventory, then access it as a reference simultaneously from multiple threads.

The flaw was corrected by enforcing that data submitted by the caller into inventory is `Sync`.

## References
- https://github.com/dtolnay/inventory/pull/42
- https://github.com/dtolnay/inventory/commit/e1e347d2725b9c9dd4a70b63eb08532ca9687652
- https://github.com/dtolnay/inventory
- https://rustsec.org/advisories/RUSTSEC-2023-0058.html
