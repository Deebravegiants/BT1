# [?] Guard EraE/eth_subscribe overflow, drop pre-ulong leftovers, cover gas-limit reject arm (#12178)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2026-07-03
Source: https://github.com/NethermindEth/nethermind/commit/58d7d9214acd1d4ad8888cabd2ad89983737e03b
Type: security-commit

## Details
Guard EraE/eth_subscribe overflow, drop pre-ulong leftovers, cover gas-limit reject arm (#12178)

* Align EraE resume buffer size underflow check with Era1

* Harden eth_subscribe to gracefully handle overlow

* Remove letfovers of pre ulong times

* Improve tests
