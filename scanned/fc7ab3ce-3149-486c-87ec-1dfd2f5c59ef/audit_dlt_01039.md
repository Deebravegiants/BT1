# [M] Denial of service via HAMT Decoding Panics

## Summary
Severity: Medium
Chain: github.com/ipfs/go-unixfs
Component: github.com/ipfs/go-unixfs
CVE: CVE-2023-23625
CWE: Uncontrolled Resource Consumption
Published: 2023-02-10
Source: https://github.com/advisories/GHSA-q264-w97q-q778
Type: github-advisory

## Details
### Impact
Trying to read malformed HAMT sharded directories can cause panics and virtual memory leaks.
If you are reading untrusted user input, an attacker can then trigger a panic.

This is caused by bogus `fanout` parameter in the HAMT directory nodes.
This include checks returned in [ipfs/go-bitfield GHSA-2h6c-j3gf-xp9r](https://github.com/ipfs/go-bitfield/security/advisories/GHSA-2h6c-j3gf-xp9r), as well as limiting the `fanout` to `<= 1024` (to avoid attempts of arbitrary sized allocations).

### Patches
- https://github.com/ipfs/go-unixfs/commit/dbcc43ec3e2db0d01e8d80c55040bba3cf22cb4b

### Workarounds
Do not feed untrusted user data to the decoding functions.

### References
- https://github.com/ipfs/go-bitfield/security/advisories/GHSA-2h6c-j3gf-xp9r
