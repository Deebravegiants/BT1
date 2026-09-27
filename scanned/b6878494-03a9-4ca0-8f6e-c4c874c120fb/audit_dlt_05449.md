# [?] fix: avoid light-client panic on frozen block body metadata

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2026-06-02
Source: https://github.com/nervosnetwork/ckb/commit/8c80639c49f568a3a57f47f6e52cac98144c87fe
Type: security-commit

## Details
fix: avoid light-client panic on frozen block body metadata

When the freezer prunes historical block body data from RocksDB,
get_block_uncles() and get_block_extension() return None for frozen
blocks.  The light-client proof handlers called .expect() on these,
causing a panic on valid remote requests.

Use snapshot.get_block() instead, which already checks freezer.number()
and reads from the append-only freezer files when the block has been
frozen.  The BlockView reconstructed from freezer data carries the same
calc_uncles_hash() and extension() values.
