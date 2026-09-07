# [?] core/rawdb: fix data race between Retrieve and Close (#20919)

## Summary
Severity: Unknown
Chain: Scroll
Component: scroll-tech/go-ethereum
Published: 2020-04-14
Source: https://github.com/scroll-tech/go-ethereum/commit/2a836bb259c03626e5ef8435f99f341ea911bfff
Type: security-commit

## Details
core/rawdb: fix data race between Retrieve and Close (#20919)

* core/rawdb: fixed data race between retrieve and close

closes https://github.com/ethereum/go-ethereum/issues/20420

* core/rawdb: use non-atomic load while holding mutex
