# [?] fix(rpc): reserve header and tx count space in block templates (GHSA-95m2-vx53-v2jw)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-07-17
Source: https://github.com/ZcashFoundation/zebra/commit/b23dfeacdce82c5505f4c0f2590b329c98786c5f
Type: security-commit

## Details
fix(rpc): reserve header and tx count space in block templates (GHSA-95m2-vx53-v2jw)

The ZIP-317 transaction selector budgeted mempool transactions against
the full MAX_BLOCK_BYTES, subtracting only the coinbase transaction.
The block header (1,487 bytes on Mainnet and Testnet) and the
transaction-count CompactSize also count toward MAX_BLOCK_BYTES, so a
template whose transactions filled that margin assembled into a block
over the consensus size limit, and every node rejected the solved
block, wasting the miner's proof-of-work.

Reserve the network-specific serialized header size and the widest
transaction count a full block can reach before admitting the coinbase
and mempool transactions.

Adds Header::serialized_size and Solution::serialized_size to
zebra-chain, a test pinning them to real header serialization on all
networks, and boundary tests proving a transaction exactly filling the
safe budget is selected while one byte more is not.
