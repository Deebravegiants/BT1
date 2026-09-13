# [?] Fix data availability checker race condition causing partial data columns to be served over RPC (#7961)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2025-09-02
Source: https://github.com/sigp/lighthouse/commit/eef02afc9326c5e7f1855a995debdbcc481f5c14
Type: security-commit

## Details
Fix data availability checker race condition causing partial data columns to be served over RPC (#7961)

Partially resolves #6439, an simpler alternative to #7931.

Race condition occurs when RPC data columns arrives after a block has been imported and removed from the DA checker:
1. Block becomes available via gossip
2. RPC columns arrive and pass fork choice check (block hasn't been imported)
3. Block import completes (removing block from DA checker)
4. RPC data columns finish verification and get imported into DA checker

This causes two issues:
1. **Partial data serving**: Already imported components get re-inserted, potentially causing LH to serve incomplete data
2. **State cache misses**: Leads to state reconstruction, holding the availability cache write lock longer and increasing race likelihood

### Proposed Changes

1. Never manually remove pending components from DA checker. Components are only removed via LRU eviction as finality advances. This makes sure we don't run into the issue described above.
2. Use `get` instead of `pop` when recovering the executed block, this prevents cache misses in race condition. This should reduce the likelihood of the race condition
3. Refactor DA checker to drop write lock as soon as components are added. This should also reduce the likelihood of the race condition

**Trade-offs:**

This solution eliminates a few nasty race conditions while allowing simplicity, with the cost of allowing block re-import (already existing).

The increase in memory in DA checker can be partially offset by a reduction in block cache size if this really comes an issue (as we now serve recent blocks from DA checker).
