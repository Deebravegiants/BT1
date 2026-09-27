# [M] `FilterRepository` stores all installed log/block/pending-tx filters in an unbounded `ConcurrentHashMap`

## Summary
Severity: Medium
Chain: Ethereum
Component: hyperledger/besu
Published: 2026-08-14
Source: https://github.com/besu-eth/besu/security/advisories/GHSA-vff7-xxjc-rccp
Type: github-advisory

## Details
FilterRepository stores all installed log/block/pending-tx filters in an unbounded ConcurrentHashMap. There is no per-connection, per-user, or global cap on the number of filters that can be created; combined with eth_newFilter/eth_newBlockFilter/eth_newPendingTransactionFilter requiring no polling to stay live, a single unauthenticated HTTP client could grow server-side memory without bound. This is CertiK finding HYB-08 (Minor; Besu's own severity assessment is medium, left unchanged). Fixed by adding a configurable cap on concurrently-active filters (--rpc-max-active-filters, default 1000) enforced at creation time, throwing FilterCountExceededException once the cap is hit, plus a configurable expiry (--rpc-filter-timeout-seconds) so unpolled filters are automatically removed. Fixed in Besu 26.7.1 by commit bf2a94134cd3a05fa5b1458e2dc199ae76bf23b2 (besu-eth/besu PR #10893).
