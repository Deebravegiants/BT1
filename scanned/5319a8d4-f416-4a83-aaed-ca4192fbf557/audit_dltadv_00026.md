# [M] Denial of service via HAMT decoding panic in github.com/ipfs/go-unixfs

## Summary
Severity: Medium
Advisory: GO-2023-1557
Aliases: CVE-2023-23625, GHSA-q264-w97q-q778
Package: github.com/ipfs/go-unixfs
Published: 2023-02-14
Source: https://osv.dev/vulnerability/GO-2023-1557
Type: chain-advisory

## Affected
- Go: `github.com/ipfs/go-unixfs` — affected >=0 <0.4.3

## Details
Trying to read malformed HAMT sharded directories can cause panics and virtual memory leaks. If you are reading untrusted user input, an attacker can then trigger a panic.

This is caused by bogus "fanout" parameter in the HAMT directory nodes. A workaround is to not feed untrusted user data to the decoding functions.

## References
- https://github.com/advisories/GHSA-q264-w97q-q778
- https://github.com/ipfs/go-unixfs/commit/467d139a640ecee4f2e74643dafcc58bb3b54175
