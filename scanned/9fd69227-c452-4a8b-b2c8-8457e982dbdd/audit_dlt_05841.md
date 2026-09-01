# [?] fix(chainindex): fix nil deref in recompute closure and handle large reconciliation gaps (#13552)

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/lotus
Published: 2026-03-31
Source: https://github.com/filecoin-project/lotus/commit/8f8f62269b342a2ec369ab224e621d0982eb84e8
Type: security-commit

## Details
fix(chainindex): fix nil deref in recompute closure and handle large reconciliation gaps (#13552)

* fix(chainindex): fix nil deref in recompute closure and handle large reconciliation gaps

1. Fix nil pointer dereference in loadExecutedMessages where the recompute
   closure captured the outer err variable by reference.

2. When the chain index is too far behind chain head (beyond
   MaxReconcileTipsets), reconciliation would attempt a massive single-
   transaction backfill causing "database is locked" failures and preventing
   node startup. Detect the gap early and enter a degraded mode where reads
   return ErrBackfillRequired but ChainValidateIndex and Apply/Revert still
   function.
