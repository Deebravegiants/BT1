# [H] nimiq-primitives: Node crash due to missing interlink validation in election macro block proposals

## Summary
Severity: High
Chain: nimiq-primitives
Component: nimiq-primitives
CVE: CVE-2026-34065
CWE: Unchecked Return Value, Improper Handling of Exceptional Conditions
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-7c4j-2m43-2mgh
Type: github-advisory

## Details
### Impact
An untrusted p2p peer can cause a node to panic by announcing an election macro block whose `validators` set contains an invalid compressed BLS voting key.

Hashing an election macro header hashes `validators` and reaches `Validators::voting_keys()`, which calls `validator.voting_key.uncompress().unwrap()` and panics on invalid bytes.

### Patches
[The patch for this vulnerability](https://github.com/nimiq/core-rs-albatross/commit/e10eaebcd7774e5da6d0ff5e88ed13503474f0ff) is included as part of [v1.3.0](https://github.com/nimiq/core-rs-albatross/releases/tag/v1.3.0).

### Workarounds
No known workarounds.
