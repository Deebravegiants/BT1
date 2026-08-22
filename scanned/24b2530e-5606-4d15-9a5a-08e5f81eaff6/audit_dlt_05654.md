# [?] Fix makeslice panic in blob versioned-hash filtering for duplicate commitments (#17199)

## Summary
Severity: Unknown
Chain: Ethereum
Component: prysmaticlabs/prysm
Published: 2026-07-17
Source: https://github.com/OffchainLabs/prysm/commit/5744c60727b5b509f6ed65dd4a136ba0a98863e3
Type: security-commit

## Details
Fix makeslice panic in blob versioned-hash filtering for duplicate commitments (#17199)

**What type of PR is this?**

Bug fix

**What does this PR do? Why is it needed?**

`GET /eth/v1/beacon/blobs/{block_id}?versioned_hashes=<vh>` panics with
`runtime error: makeslice: cap out of range` when a requested versioned
hash
matches a KZG commitment that appears more than once in the target block
(legal per consensus rules — e.g. mainnet slot 8626186 carries the same
commitment three times). net/http recovers the panic per-request, so the
node
survives, but every such request aborts with a connection reset and a
panic
stack in the logs. Remotely triggerable on any node whose block DB
contains a
duplicate-commitment block: hash matching runs before any blob-storage
access, so blob pruning does not prevent it.

Root cause, in `resolveBlobsContext`
(`beacon-chain/rpc/lookup/blocker.go`):
requested hashes are deduplicated into a set, but `indices` receives one
entry per *matching commitment*. The missing-hash detection then
compares
raw counts:

    if len(indices) != len(cfg.VersionedHashes) {
missingHashes := make([]string, 0,
len(cfg.VersionedHashes)-len(indices)) // negative cap → panic

One requested hash matching N≥2 duplicate commitments makes the capacity
negative. The same count heuristic causes two more defects:

- A client repeating a hash in the query gets a spurious 404 with an
empty

_Trimmed to 38 lines — full report: https://github.com/OffchainLabs/prysm/commit/5744c60727b5b509f6ed65dd4a136ba0a98863e3_
