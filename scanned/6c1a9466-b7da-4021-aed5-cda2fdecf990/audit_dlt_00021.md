# [H] A single devp2p peer can drive unbounded block-fetch work via repeated NEW_BLOCK_HASHES/NEW_BLOCK announcements for the same block number

## Summary
Severity: High
Chain: Ethereum
Component: hyperledger/besu
Published: 2026-08-14
Source: https://github.com/besu-eth/besu/security/advisories/GHSA-j2j5-x2rr-cv75
Type: github-advisory

## Details
A peer that completes the eth/68 handshake could drive uncontrolled scheduled block-fetch work (memory and threads) over the default devp2p surface, with no JSON-RPC/WebSocket required, by sending many different hashes for the same block number. This is CertiK finding HYB-01 (Major, NEW_BLOCK_HASHES fan-out) and HYB-04 (Medium, NEW_BLOCK unknown-parent retrieval). Fixed by tracking requested blocks in a SortedMap keyed by block number, so a second announcement for an already-requested number is accepted only from a strictly-better-reputation peer, bounding outstanding work to roughly (connected peers x propagation range). Fixed in Besu 26.7.1 by commit d8033caea93d96165f5aa9699123b99eebc09033 (besu-eth/besu PR #10892).
