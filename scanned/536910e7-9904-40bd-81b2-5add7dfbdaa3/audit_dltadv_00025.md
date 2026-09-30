# [H] Panic in github.com/ipfs/go-merkledag

## Summary
Severity: High
Advisory: GO-2022-1155
Aliases: CVE-2022-23495, GHSA-x39j-h85h-3f46
Package: github.com/ipfs/go-merkledag
Published: 2022-12-22
Source: https://osv.dev/vulnerability/GO-2022-1155
Type: chain-advisory

## Affected
- Go: `github.com/ipfs/go-merkledag` — affected >=0.4.0 <0.8.1

## Details
A ProtoNode may be modified in such a way as to cause various encode errors which will trigger a panic on common method calls that don't allow for error returns.

Additionally, use of the ProtoNode.SetCidBuilder() method to set non-functioning CidBuilder (such as one that refers to a multihash where an implementation of that hash function is not available) may cause the same methods to panic as a new CID is required but cannot be created.

## References
- https://github.com/ipfs/go-merkledag/security/advisories/GHSA-x39j-h85h-3f46
- https://github.com/ipfs/kubo/issues/9297
- https://github.com/ipfs/go-merkledag/issues/90
- https://github.com/ipfs/go-merkledag/pull/91
- https://github.com/ipfs/go-merkledag/pull/92
- https://github.com/ipfs/go-merkledag/pull/93
