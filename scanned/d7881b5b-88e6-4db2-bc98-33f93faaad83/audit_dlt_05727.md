# [?] fix(mempool): Avoid panicking when a transaction is unexpectedly missing in the mempool (#10049)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2025-11-13
Source: https://github.com/ZcashFoundation/zebra/commit/333f4ffc865096260bea398f0d524a3fa9b5eb86
Type: security-commit

## Details
fix(mempool): Avoid panicking when a transaction is unexpectedly missing in the mempool (#10049)

* Logs a warnings when a dependent transaction id is unexpectedly missing from the mempool's verified set instead of panicking

* - Fixes an issue in `mempool::storage::VerifiedSet::remove_all_that()` where the method could attempt to remove the same transaction twice if it depended on the outputs of another transaction that was just removed.
- Fixes an issue where mined transaction dependencies were not being removed from the mempool's transaction dependencies.

* fixes clippy lint

* Updates `TransactionDependencies::remove_all()` to remove tracked dependent transaction ids for a transaction when removing those dependent transaction.

Updates `clear_mined_dependencies()` to remove keys in the `dependencies` map with empty values.
