# [?] triedb/pathdb: fix index out of range panic in decodeSingle (#32937)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2025-10-20
Source: https://github.com/ethereum/go-ethereum/commit/11c0fb98af8ba14deb6abe77b357cbe927ba05ba
Type: security-commit

## Details
triedb/pathdb: fix index out of range panic in decodeSingle (#32937)

Fixes TestCorruptedKeySection flaky test failure.
https://github.com/ethereum/go-ethereum/actions/runs/18600235182/job/53037084761?pr=32920
