# [H] IPFS go-unixfsnode subject to DOS via HAMT Decoding Panics

## Summary
Severity: High
Chain: github.com/ipfs/go-unixfsnode
Component: github.com/ipfs/go-unixfsnode
CVE: CVE-2023-23631
CWE: Uncontrolled Resource Consumption
Published: 2023-02-10
Source: https://github.com/advisories/GHSA-4gj3-6r43-3wfc
Type: github-advisory

## Details
## Impact

Trying to read malformed HAMT sharded directories can cause panics and virtual memory leaks.
If you are reading untrusted user input, an attacker can then trigger a panic.

This is caused by a bogus fanout parameter in the HAMT directory nodes.
This includes checks returned in [ipfs/go-bitfield GHSA-2h6c-j3gf-xp9r](https://github.com/ipfs/go-bitfield/security/advisories/GHSA-2h6c-j3gf-xp9r), as well as limiting the fanout to <= 1024 (to avoid attempts of arbitrary sized allocations).

## Patches
- https://github.com/ipfs/go-unixfsnode/commit/91b3d39d33ef0cd2aff2c95d50b2329350944b68
- https://github.com/ipfs/go-unixfsnode/commit/a4ed723727e0bdc2277158337c2fc0d82802d122

## References

* https://github.com/ipfs/go-unixfs/security/advisories/GHSA-q264-w97q-q778
* https://github.com/ipfs/go-bitfield/security/advisories/GHSA-2h6c-j3gf-xp9r
