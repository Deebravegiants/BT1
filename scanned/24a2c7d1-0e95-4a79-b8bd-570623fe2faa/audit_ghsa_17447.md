# [H] Babylon Nil BlockHash in BLS vote extensions triggers panics in consensus handlers

## Summary
Severity: High
Advisory: GHSA-m6wq-66p2-c8pc
CWE: CWE-476
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-12-08
Source: https://github.com/advisories/GHSA-m6wq-66p2-c8pc
Type: github-advisory

## Affected
- Go: `github.com/babylonlabs-io/babylon/v4` — affected >=0 <4.2.0
- Go: `github.com/babylonlabs-io/babylon/v3` — affected >=0
- Go: `github.com/babylonlabs-io/babylon/v2` — affected >=0
- Go: `github.com/babylonlabs-io/babylon` — affected >=0

## Details
### Summary

A vulnerability exists in Babylon’s BLS vote extension processing where a malicious active validator can submit a VoteExtension with the `block_hash` field omitted from the protobuf serialization. Because protobuf fields are optional, unmarshalling succeeds but leaves `BlockHash` as nil. Babylon then dereferences this nil pointer in consensus-critical code paths (notably `VerifyVoteExtension`, and also proposal-time vote verification), causing a runtime panic.

### Impact

Intermittent validator crashes at epoch boundaries, which would slow down the creation of the epoch boundary block.

### Finder 

Vulnerability discovered by:

- @GrumpyLaurie55348

## References
- https://github.com/babylonlabs-io/babylon/security/advisories/GHSA-m6wq-66p2-c8pc
- https://github.com/babylonlabs-io/babylon/commit/f79ad58c1d5bcab3451cb7a47c91e713935917d7
- https://github.com/babylonlabs-io/babylon
