# [?] triedb/pathdb: fix an deadlock in history indexer (#32260)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2025-07-23
Source: https://github.com/ethereum/go-ethereum/commit/16117eb7cddc4584865af106d2332aa89f387d3d
Type: security-commit

## Details
triedb/pathdb: fix an deadlock in history indexer (#32260)

Seems the `signal.result` was not sent back in shorten case, this will
cause a deadlock.

---------

Signed-off-by: jsvisa <delweng@gmail.com>
Co-authored-by: Gary Rong <garyrong0905@gmail.com>
