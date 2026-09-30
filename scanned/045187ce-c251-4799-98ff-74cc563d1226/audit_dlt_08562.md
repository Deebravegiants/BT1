# [?] Fix apply phase invariant race condition

## Summary
Severity: Unknown
Chain: Stellar
Component: stellar/stellar-core
Published: 2025-07-16
Source: https://github.com/stellar/stellar-core/commit/264e018cd43e774527d856e76266ed69830b264c
Type: security-commit

## Details
Fix apply phase invariant race condition

## Patch
### src/invariant/test/BucketListIsConsistentWithDatabaseTests.cpp
```diff
@@ -58,6 +58,7 @@ struct BucketListGenerator
     {
         std::map<std::string, std::shared_ptr<LiveBucket>> buckets;
         auto has = getHistoryArchiveState(app);
+        app->getLedgerManager().markApplyStateReset();
         auto& wm = app->getWorkScheduler();
         wm.executeWork<T>(buckets, has,
                           app->getConfig().LEDGER_PROTOCOL_VERSION,
```

### src/ledger/LedgerManagerImpl.cpp
```diff
@@ -1338,8 +1338,6 @@ LedgerManagerImpl::ledgerCloseComplete(uint32_t lcl, bool calledViaExternalize,
         mApp.getHerder().lastClosedLedgerIncreased(
             appliedLatest, ledgerData.getTxSet(), upgradeApplied);
     }
-
-    mApplyState.markEndOfCommitting();
 }
 
 void
@@ -1720,6 +1718,12 @@ LedgerManagerImpl::applyLedger(LedgerCloseData const& ledgerData,
             mApplyState.getSorobanNetworkConfigForCommit());
     }
 
+    // At this point, we've committed all changes to the Apply State for this
+    // ledger. While the following functions will publish this state to other
+    // subsystems, that's not relevant for Apply State phases since ApplyState
+    // is only accessed by LedgerManager's apply threads.
+    mApplyState.markEndOfCommitting();
+
     // Steps 5, 6, 7 are done in `advanceLedgerStateAndPublish`
     // NB: appliedLedgerState is invalidated after this call.
     if (threadIsMain())
```
