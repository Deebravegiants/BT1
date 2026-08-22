# [?] Fix deadlock when creating the DataLayer wallet during sync (#21225)

## Summary
Severity: Unknown
Chain: Chia
Component: Chia-Network/chia-blockchain
Published: 2026-08-04
Source: https://github.com/Chia-Network/chia-blockchain/commit/d1d9a2b40b29cca03eae9e37d5e05dfe3f4a8a55
Type: security-commit

## Details
Fix deadlock when creating the DataLayer wallet during sync (#21225)

The wallet sync path holds WalletStateManager.lock for the duration of
sync. When _add_coin_states discovers a DataLayer launcher and no
DataLayer wallet exists yet, it called
get_dl_wallet(create_if_not_found=True), which re-acquires the same
non-reentrant asyncio.Lock, deadlocking the sync task. Create the
wallet directly at the sync call site instead, leaving get_dl_wallet
unchanged for RPC callers.

Regression from #20320 (baf8bd05c0).
