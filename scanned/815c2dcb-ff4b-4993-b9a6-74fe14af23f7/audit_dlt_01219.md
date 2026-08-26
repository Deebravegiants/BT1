# [?] cl/sentinel: fix panic on short attnets ENR entry (#20492)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-04-11
Source: https://github.com/erigontech/erigon/commit/933f98664152b7dd1004e65cef6ce0e38e33b9b5
Type: security-commit

## Details
cl/sentinel: fix panic on short attnets ENR entry (#20492)

## Summary
Fixes a panic seen in the wild:

```
panic: runtime error: index out of range [4] with length 1
  cl/sentinel.(*Sentinel).findPeersForSubnets.func1
        cl/sentinel/discovery.go:80
```

A malformed/short `attnets` ENR entry decodes into a
`bitfield.Bitvector64` shorter than the expected 8 bytes, so indexing
`peerSubnets[subnetIdx/8]` goes out of range when `subnetIdx >= 8`.

Adds a `len(peerSubnets) == 8` guard at all three call sites in
`cl/sentinel/discovery.go` (`findPeersForSubnets` filter, post-connect
coverage update, and `onConnection` underserved-subnet check).
