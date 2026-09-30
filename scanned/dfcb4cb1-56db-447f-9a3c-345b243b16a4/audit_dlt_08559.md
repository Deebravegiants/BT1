# [?] Fix race condition in rebuildInMemorySorobanStateForTesting

## Summary
Severity: Unknown
Chain: Stellar
Component: stellar/stellar-core
Published: 2026-07-15
Source: https://github.com/stellar/stellar-core/commit/911fa9112c7a381ecf5f465825e52c5f1b82516e
Type: security-commit

## Details
Fix race condition in rebuildInMemorySorobanStateForTesting

## Patch
### src/ledger/LedgerManagerImpl.cpp
```diff
@@ -896,6 +896,13 @@ LedgerManagerImpl::getInMemorySorobanStateForTesting()
 void
 LedgerManagerImpl::rebuildInMemorySorobanStateForTesting(uint32_t ledgerVersion)
 {
+    // Make sure we don't race on an in-progress compilation.
+    if (mApplyState.isCompilationRunning())
+    {
+        mApplyState.finishPendingCompilation();
+        mApplyState.markEndOfSetupPhase();
+    }
+
     mApplyState.resetToSetupPhase();
     mApplyState.getInMemorySorobanStateForTesting().clearForTesting();
     mApplyState.populateInMemorySorobanState();
```
