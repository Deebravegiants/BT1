# [M] ic-stable-structures vulnerable to BTreeMap memory leak when deallocating nodes with overflows

## Summary
Severity: Medium
Advisory: GHSA-3rcq-39xp-7xjp
CVE: CVE-2024-4435
CWE: CWE-401
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-05-21
Source: https://github.com/advisories/GHSA-3rcq-39xp-7xjp
Type: github-advisory

## Affected
- crates.io: `ic-stable-structures` — affected >=0.6.0 <0.6.4

## Details
### Impact
When storing unbounded types in a `BTreeMap`, a node is represented as a linked list of "memory chunks". It was discovered recently that when we deallocate a node, in some cases only the first memory chunk is deallocated, and the rest of the memory chunks remain (incorrectly) allocated, causing a memory leak.

In the worst case, depending on how a canister uses the `BTreeMap`, an adversary could interact with the canister through its API and trigger interactions with the map that keep consuming memory due to the memory leak. This could potentially lead to using an excessive amount of memory, or even running out of memory. 

This issue has been fixed in #212 by changing the logic for deallocating nodes to ensure that all of a node's memory chunks are deallocated. Tests have been added to prevent regressions of this nature moving forward.

**Note:** Users of stable-structure < 0.6.0 are not affected.

### Patches
The problem has been fixed in PR #212 and users are asked to upgrade to version `0.6.4`.

### Workarounds
Users who are not storing unbounded types in `BTreeMap` are not affected and do not need to upgrade. Otherwise, an upgrade to version `0.6.4` is necessary.

## References
- https://github.com/dfinity/stable-structures/security/advisories/GHSA-3rcq-39xp-7xjp
- https://nvd.nist.gov/vuln/detail/CVE-2024-4435
- https://github.com/dfinity/stable-structures/pull/212
- https://github.com/dfinity/stable-structures/commit/4f6b8ae521884833498bae26369c353c10f28ea7
- https://docs.rs/ic-stable-structures/0.6.4/ic_stable_structures
- https://github.com/dfinity/stable-structures
- https://internetcomputer.org/docs/current/developer-docs/smart-contracts/maintain/storage#stable-memory
- https://rustsec.org/advisories/RUSTSEC-2024-0406.html
