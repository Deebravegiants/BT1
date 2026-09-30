# [?] Fix minor race condition in invariant check

## Summary
Severity: Unknown
Chain: Stellar
Component: stellar/stellar-core
Published: 2026-02-17
Source: https://github.com/stellar/stellar-core/commit/ce4b6e80b977e4158bf557bff78ad9db268020f0
Type: security-commit

## Details
Fix minor race condition in invariant check

## Patch
### src/herder/test/HerderTests.cpp
```diff
@@ -5176,6 +5176,8 @@ TEST_CASE("ledger state update flow with parallel apply", "[herder][parallel]")
                 REQUIRE(lm.getLastClosedLedgerNum() == lcl);
                 REQUIRE(lm.getLastClosedLedgerHAS().currentLedger ==
                         lastHeader.ledgerSeq);
+                REQUIRE(lm.copyLedgerStateSnapshot().getLedgerHeader() ==
+                        lastHeader);
 
                 // Apply state got committed, but has not yet been propagated to
                 // read-only state
@@ -5227,6 +5229,8 @@ TEST_CASE("ledger state update flow with parallel apply", "[herder][parallel]")
                 auto readOnly = lm.getLastClosedLedgerHeader();
                 REQUIRE(readOnly.header.ledgerSeq == lcl + 1);
                 REQUIRE(lm.getLastClosedLedgerNum() == lcl + 1);
+                REQUIRE(lm.copyLedgerStateSnapshot().getLedgerHeader() ==
+                        readOnly.header);
                 auto has = lm.getLastClosedLedgerHAS();
                 REQUIRE(has.currentLedger == readOnly.header.ledgerSeq);
 
```

### src/invariant/InvariantManagerImpl.cpp
```diff
@@ -191,8 +191,7 @@ InvariantManagerImpl::checkOnLedgerCommit(
         auto message = fmt::format(
             FMT_STRING(R"(Invariant "{}" does not hold on ledger commit: {})"),
             invariant->getName(), result);
-        onInvariantFailure(invariant, message,
-                           lclSnapshot.getLedgerSeq() + 1);
+        onInvariantFailure(invariant, message, lclSnapshot.getLedgerSeq() + 1);
     }
 }
 
```

### src/ledger/LedgerManager.h
```diff
@@ -231,14 +231,15 @@ class LedgerManager
     getLastClosedLedgerHeader() const = 0;
 
     // Create a thread-safe copy of the current canonical ledger state
-    // snapshot. Can be called from any thread.
+    // snapshot. Can be called from any thread (except for apply, which must use
+    // copyApplyLedgerStateSnapshot instead).
     virtual LedgerStateSnapshot copyLedgerStateSnapshot() const = 0;
 
     // Create a thread-safe copy of the current canonical ledger state
     // snapshot, typed as an apply-time snapshot. Used by legacy (pre-V23)
     // code paths that need an ApplyLedgerStateSnapshot but don't have
     // access to ApplyState.
-    // TODO: Refactor such that this doesn' have to be a public function
+    // TODO: Refactor such that this doesn't have to be a public function
     virtual ApplyLedgerStateSnapshot copyApplyLedgerStateSnapshot() const = 0;
 
     // Refresh `snapshot` if its ledger seq differs from the current canonical
@@ -346,9 +347,7 @@ class LedgerManager
     advanceLedgerStateAndPublish(uint32_t ledgerSeq, bool calledViaExternalize,
                                  LedgerCloseData const& ledgerData,
                                  CompleteConstLedgerStatePtr newLedgerState,
-                                 bool upgradeApplied,
-                                 std::shared_ptr<InMemorySorobanState const>
-                                     inMemorySnapshotForInvariant) = 0;
+                                 bool upgradeApplied) = 0;
 
     virtual void assertSetupPhase() const = 0;
 #ifdef BUILD_TESTS
```

### src/ledger/LedgerManagerImpl.cpp
```diff
@@ -621,9 +621,8 @@ LedgerManagerImpl::loadLastKnownLedgerInternal(bool skipBuildingFullState)
         CLOG_INFO(Perf, "Populated in-memory Soroban state in {:.3f} sec",
                   populateSecs.count());
 
-        maybeRunSnapshotInvariantFromLedgerState(
-            copyApplyLedgerStateSnapshot(), maybeCopySorobanStateForInvariant(),
-            /* runInParallel */ false);
+        maybeRunSnapshotInvariantFromLedgerState(copyApplyLedgerStateSnapshot(),
+                                                 /* runInParallel */ false);
     }
     mApplyState.markEndOfSetupPhase();
 
@@ -746,7 +745,10 @@ LedgerManagerImpl::getLastTxFee() const
 LedgerHeaderHistoryEntry const&
 LedgerManagerImpl::getLastClosedLedgerHeader() const
 {
-    releaseAssert(!mApp.threadIsType(Application::ThreadType::APPLY));
+    // Must be main thread: returns a reference into mLastClosedLedgerState,
+    // which is only replaced on the main thread (advanceLastClosedLedgerState).
+    // A cross-thread caller could hold a dangling reference after replacement.
+    releaseAssert(threadIsMain());
     SharedLockShared guard(mLedgerStateSnapshotMutex);
     releaseAssert(mLastClosedLedgerState);
     return mLastClosedLedgerState->getLastClosedLedgerHeader();
@@ -770,38 +772,24 @@ LedgerManagerImpl::getLastClosedLedgerNum() const
     return mLastClosedLedgerState->getLastClosedLedgerHeader().header.ledgerSeq;
 }
 
-std::shared_ptr<InMemorySorobanState const>
-LedgerManagerImpl::maybeCopySorobanStateForInvariant()
-{
-    std::shared_ptr<InMemorySorobanState const> inMemorySnapshotForInvariant =
-        nullptr;
-    if (mApp.getInvariantManager().shouldRunInvariantSnapshot())
-    {
-        // The in memory state copy is expensive, so we need to mark
-        // that start of the invariant scan here, not in the callback, to ensure
-        // we don't trigger a race condition that creates two copies.
-        mApp.getInvariantManager().markStartOfInvariantSnapshot();
-        inMemorySnapshotForInvariant =
-            std::make_shared<InMemorySorobanState const>(
-                mApplyState.getInMemorySorobanState());
-    }
-    return inMemorySnapshotForInvariant;
-}
-
 void
 LedgerManagerImpl::maybeRunSnapshotInvariantFromLedgerState(
-    ApplyLedgerStateSnapshot const& ledgerState,
-    std::shared_ptr<InMemorySorobanState const> inMemorySnapshotForInvariant,
-    bool runInParallel) const
+    ApplyLedgerStateSnapshot const& ledgerState, bool runInParallel)
 {
-    releaseAssert(threadIsMain());
-
-    if (!inMemorySnapshotForInvariant ||
-        !mApp.getConfig().INVARIANT_EXTRA_CHECKS || mApp.isStopping())
+    if (!mApp.getConfig().INVARIANT_EXTRA_CHECKS || mApp.isStopping() ||
+        !mApp.getInvariantManager().shouldRunInvariantSnapshot())
     {
         return;
     }
 
+    // The in memory state copy is expensive, so we need to mark the start of
+    // the invariant scan here, not in the callback, to ensure we don't trigger
+    // a race condition that creates two copies.
+    mApp.getInvariantManager().markStartOfInvariantSnapshot();
+    auto inMemorySnapshotForInvariant =
+        std::make_shared<InMemorySorobanState const>(
+            mApplyState.getInMemorySorobanState());
+
     // Verify consistency of all snapshot state.
     auto ledgerSeq = ledgerState.getLedgerSeq();
     inMemorySnapshotForInvariant->assertLastClosedLedger(ledgerSeq);
@@ -830,7 +818,10 @@ LedgerManagerImpl::maybeRunSnapshotInvariantFromLedgerState(
 SorobanNetworkConfig const&
 LedgerManagerImpl::getLastClosedSorobanNetworkConfig() const
 {
-    releaseAssert(!mApp.threadIsType(Application::ThreadType::APPLY));
+    // Must be main thread: returns a reference into mLastClosedLedgerState,
+    // which is only replaced on the main thread (advanceLastClosedLedgerState).
+    // A cross-thread caller could hold a dangling reference after replacement.
+    releaseAssert(threadIsMain());
     SharedLockShared guard(mLedgerStateSnapshotMutex);
     releaseAssert(mLastClosedLedgerState);
     releaseAssert(mLastClosedLedgerState->hasSorobanConfig());
@@ -1354,20 +1345,15 @@ getMetaIOContext(Application& app)
 } // namespace
 
 void
-LedgerManagerImpl::ledgerCloseComplete(
-    uint32_t lcl, bool calledViaExternalize, LedgerCloseData const& ledgerData,
-    bool upgradeApplied,
-    std::shared_ptr<InMemorySorobanState const> inMemorySnapshotForInvariant)
+LedgerManagerImpl::ledgerCloseComplete(uint32_t lcl, bool calledViaExternalize,
+                                       LedgerCloseData const& ledgerData,
+                                       bool upgradeApplied)
 {
     // We just finished applying `lcl`, maybe change LM's state
     // Also notify Herder so it can trigger next ledger.
 
     releaseAssert(threadIsMain());
 
-    // Kick off the snapshot invariant, if enabled
-    ApplyLedgerStateSnapshot stateCopy = mApplyState.copyLedgerStateSnapshot();
-    maybeRunSnapshotInvariantFromLedgerState(stateCopy,
-                                             inMemorySnapshotForInvariant);
     uint32_t latestHeardFromNetwork =
         mApp.getLedgerApplyManager().getLargestLedgerSeqHeard();
     uint32_t latestQueuedToApply =
@@ -1409,8 +1395,7 @@ void
 LedgerManagerImpl::advanceLedgerStateAndPublish(
     uint32_t ledgerSeq, bool calledViaExternalize,
     LedgerCloseData const& ledgerData,
-    CompleteConstLedgerStatePtr newLedgerState, bool upgradeApplied,
-    std::shared_ptr<InMemorySorobanState const> inMemorySnapshotForInvariant)
+    CompleteConstLedgerStatePtr newLedgerState, bool upgradeApplied)
 {
 #ifdef BUILD_TESTS
     if (mAdvanceLedgerStateAndPublishOverride)
@@ -1448,7 +1433,7 @@ LedgerManagerImpl::advanceLedgerStateAndPublish(
     // Maybe set LedgerManager into synced state, maybe let
     // Herder trigger next ledger
     ledgerCloseComplete(ledgerSeq, calledViaExternalize, ledgerData,
-                        upgradeApplied, inMemorySnapshotForInvariant);
+                        upgradeApplied);
     CLOG_INFO(Ledger, "Ledger close complete: {}", ledgerSeq);
 }
 
@@ -1867,29 +1852,29 @@ LedgerManagerImpl::applyLedger(LedgerCloseData const& ledgerData,
     mApplyState.markEndOfCommitting();
     JITTER_INJECT_DELAY();
 
-    // Step 5: copy the in-memory Soroban state if we should run the snapshot
-    // invariant for this ledger. At this point, commit has completed and
-    // in-memory state is immutable.
-    auto inMemorySnapshotForInvariant = maybeCopySorobanStateForInvariant();
+    // Step 5: kick off the snapshot invariant, if the timer has fired.
+    // Both the apply-state snapshot and the in-memory Soroban state are
+    // captured here at the same point (after commit), so they are guaranteed
+    // to be from the same ledger.
+    maybeRunSnapshotInvariantFromLedgerState(
+        mApplyState.copyLedgerStateSnapshot());
 
     // Steps 6, 7, 8 are done in `advanceLedgerStateAndPublish`
     // NB: appliedLedgerState is invalidated after this call.
     if (threadIsMain())
     {
         advanceLedgerStateAndPublish(ledgerSeq, calledViaExternalize,
                                      ledgerData, std::move(appliedLedgerState),
-                                     upgradeApplied,
-                                     inMemorySnapshotForInvariant);
+                                     upgradeApplied);
     }
     else
     {
         auto cb = [this, ledgerSeq, calledViaExternalize, ledgerData,
                    appliedLedgerState = std::move(appliedLedgerState),
-                   upgradeApplied, inMemorySnapshotForInvariant]() mutable {
+                   upgradeApplied]() mutable {
             advanceLedgerStateAndPublish(
                 ledgerSeq, calledViaExternalize, ledgerData,
-                std::move(appliedLedgerState), upgradeApplied,
-                inMemorySnapshotForInvariant);
+                std::move(appliedLedgerState), upgradeApplied);
         };
         mApp.postOnMainThread(std::move(cb), "advanceLedgerStateAndPublish");
     }
@@ -2215,12 +2200,12 @@ LedgerManagerImpl::updateCanonicalStateForTesting(LedgerHeader const& header)
     HistoryArchiveState has;
     has.currentLedger = header.ledgerSeq;
 
+    SharedLockExclusive lock(mLedgerStateSnapshotMutex);
     auto state =
         buildLedgerState(header, has, mLastClosedLedgerState, std::nullopt);
 
     mApplyState.setLedgerStateForTesting(state);
 
-    SharedLockExclusive lock(mLedgerStateSnapshotMutex);
     mLastClosedLedgerState = state;
 }
 #endif
@@ -3002,7 +2987,7 @@ LedgerManagerImpl::finalizeLedgerTxnChanges(
             if (isP24UpgradeLedger && gIsProductionNetwork)
             {
                 p23_hot_archive_bug::addHotArchiveBatchWithP23HotArchiveFix(
-                    ltx, mApp, lh, evictedState.archivedEntries,
+                    ltx, mApp, lclSnapshot, lh, evictedState.archivedEntries,
                     restoredHotArchiveKeys);
             }
             else
@@ -3016,7 +3001,8 @@ LedgerManagerImpl::finalizeLedgerTxnChanges(
                 {
                     mApp.getProtocol23CorruptionDataVerifier()
                         ->verifyArchivalOfCorruptedEntry(
-                            evictedState, mApp, lh.ledgerSeq, lh.ledgerVersion);
+                            evictedState, lclSnapshot, lh.ledgerSeq,
+                            lh.ledgerVersion);
                 }
             }
         }
```

### src/ledger/LedgerManagerImpl.h
```diff
@@ -405,22 +405,12 @@ class LedgerManagerImpl : public LedgerManager
     storePersistentStateAndLedgerHeaderInDB(LedgerHeader const& header,
                                             bool appendToCheckpoint);
 
-    // Copies in-memory Soroban state for snapshot invariant if required for
-    // this ledger, or returns nullptr otherwise. Should be called in
-    // READY_TO_APPLY phase when InMemorySorobanState is read only.
-    // Also clears the snapshot trigger flag to prevent race conditions.
-    std::shared_ptr<InMemorySorobanState const>
-    maybeCopySorobanStateForInvariant();
-
-    // Trigger snapshot invariant on background thread if
-    // inMemorySnapshotForInvariant is not null.
-    // If runInParallel is false, runs on the calling thread (this is useful in
-    // certain scenarios such as startup)
+    // If the invariant timer has fired, copies the in-memory Soroban state and
+    // the apply-state snapshot, then kicks off the snapshot invariant check.
+    // If runInParallel is false, runs on the calling thread (useful at
+    // startup).
     void maybeRunSnapshotInvariantFromLedgerState(
-        ApplyLedgerStateSnapshot const& ledgerState,
-        std::shared_ptr<InMemorySorobanState const>
-            inMemorySnapshotForInvariant,
-        bool runInParallel = true) const;
+        ApplyLedgerStateSnapshot const& ledgerState, bool runInParallel = true);
 
     static void prefetchTransactionData(AbstractLedgerTxnParent& rootLtx,
                                         ApplicableTxSetFrame const& txSet,
@@ -558,17 +548,14 @@ class LedgerManagerImpl : public LedgerManager
 
     void applyLedger(LedgerCloseData const& ledgerData,
                      bool calledViaExternalize) override;
-    void advanceLedgerStateAndPublish(
-        uint32_t ledgerSeq, bool calledViaExternalize,
-        LedgerCloseData const& ledgerData,
-        CompleteConstLedgerStatePtr newLedgerState, bool queueRebuildNeeded,
-        std::shared_ptr<InMemorySorobanState const>
-            inMemorySnapshotForInvariant = nullptr) override;
+    void
+    advanceLedgerStateAndPublish(uint32_t ledgerSeq, bool calledViaExternalize,
+                                 LedgerCloseData const& ledgerData,
+                                 CompleteConstLedgerStatePtr newLedgerState,
+                                 bool queueRebuildNeeded) override;
     void ledgerCloseComplete(uint32_t lcl, bool calledViaExternalize,
                              LedgerCloseData const& ledgerData,
-                             bool queueRebuildNeeded,
-                             std::shared_ptr<InMemorySorobanState const>
-                                 inMemorySnapshotForInvariant);
+                             bool queueRebuildNeeded);
     void setLastClosedLedger(LedgerHeaderHistoryEntry const& lastClosed,
                              bool rebuildInMemoryState) override;
 
```

### src/ledger/LedgerTxn.cpp
```diff
@@ -2756,10 +2756,10 @@ LedgerTxnRoot::Impl::Impl(Application& app,
     , mEntryCache(entryCacheSize)
     , mBulkLoadBatchSize(prefetchBatchSize)
     , mChild(nullptr)
+    , mThreadInvariant()
 #ifdef BEST_OFFER_DEBUGGING
     , mBestOfferDebuggingEnabled(bestOfferDebuggingEnabled)
 #endif
-    , mThreadInvariant()
 {
 }
 
```

### src/ledger/P23HotArchiveBug.cpp
```diff
@@ -7,13 +7,11 @@
 #include <array>
 #include <string>
 
-#include "bucket/BucketListSnapshot.h"
 #include "bucket/BucketManager.h"
 #include "bucket/BucketUtils.h"
-#include "ledger/LedgerManager.h"
+#include "ledger/LedgerStateSnapshot.h"
 #include "ledger/LedgerTxn.h"
 #include "ledger/LedgerTxnImpl.h"
-#include "main/AppConnector.h"
 #include "main/Application.h"
 #include <xdrpp/printer.h>
 
@@ -36,7 +34,8 @@ using namespace internal;
 
 void
 addHotArchiveBatchWithP23HotArchiveFix(
-    AbstractLedgerTxn& ltx, Application& app, LedgerHeader header,
+    AbstractLedgerTxn& ltx, Application& app,
+    ApplyLedgerStateSnapshot const& snapshot, LedgerHeader header,
     std::vector<LedgerEntry> const& archivedEntries,
     std::vector<LedgerKey> const& restoredEntries)
 {
@@ -49,7 +48,6 @@ addHotArchiveBatchWithP23HotArchiveFix(
     auto updatedArchivedEntries = archivedEntries;
     updatedArchivedEntries.reserve(updatedArchivedEntries.size() +
                                    P23_CORRUPTED_HOT_ARCHIVE_ENTRIES_COUNT);
-    auto snap = app.getAppConnector().copyLedgerStateSnapshot();
     for (size_t i = 0; i < P23_CORRUPTED_HOT_ARCHIVE_ENTRIES_COUNT; ++i)
     {
         LedgerEntry corruptedEntry =
@@ -67,7 +65,7 @@ addHotArchiveBatchWithP23HotArchiveFix(
         // Hot Archive that match our expectations for the corrupted entries.
 
         // Ensure that the entry exists in Hot Archive.
-        auto hotArchiveEntry = snap.loadArchiveEntry(corruptedEntryKey);
+        auto hotArchiveEntry = snapshot.loadArchiveEntry(corruptedEntryKey);
         if (!hotArchiveEntry)
         {
             CLOG_WARNING(
@@ -336,8 +334,9 @@ Protocol23CorruptionDataVerifier::verifyRestorationOfCorruptedEntry(
 
 void
 Protocol23CorruptionDataVerifier::verifyArchivalOfCorruptedEntry(
-    EvictedStateVectors const& evictedState, Application& app,
-    uint32_t ledgerSeq, uint32_t protocolVersion)
+    EvictedStateVectors const& evictedState,
+    ApplyLedgerStateSnapshot const& snapshot, uint32_t ledgerSeq,
+    uint32_t protocolVersion)
 {
     if (!protocolVersionEquals(protocolVersion, ProtocolVersion::V_23))
     {
@@ -347,11 +346,6 @@ Protocol23CorruptionDataVerifier::verifyArchivalOfCorruptedEntry(
     // p23 we haven't increased the number of threads.
     std::lock_guard<std::mutex> lock(mMutex);
 
-    // This database can load the actual, correct version of a
-    // given ledger key. This tells us the value that should
-    // have been evicted.
-    auto snap = app.getLedgerManager().copyLedgerStateSnapshot();
-
     // This is the set of all keys incorrectly evicted for this
     // ledger
     auto evictedKeysIter = mEvictedSeqToKeys.find(ledgerSeq);
@@ -365,7 +359,7 @@ Protocol23CorruptionDataVerifier::verifyArchivalOfCorruptedEntry(
     {
         // Load the correct value from the live database.
         auto evictedLedgerKey = LedgerEntryKey(evictedEntry);
-        auto databaseEntry = snap.loadLiveEntry(evictedLedgerKey);
+        auto databaseEntry = snapshot.loadLiveEntry(evictedLedgerKey);
         releaseAssert(databaseEntry != nullptr);
 
         // If there was a corruption
```

### src/ledger/P23HotArchiveBug.h
```diff
@@ -18,6 +18,7 @@ namespace stellar
 {
 class Application;
 class AbstractLedgerTxn;
+class ApplyLedgerStateSnapshot;
 class Config;
 struct EvictedStateVectors;
 
@@ -86,9 +87,11 @@ class Protocol23CorruptionDataVerifier
     // This should be called for every eviction that occurs during catchup,
     // non-corrupted evictions are ignored.
     // This is thread-safe.
-    void verifyArchivalOfCorruptedEntry(EvictedStateVectors const& evictedState,
-                                        Application& app, uint32_t ledgerSeq,
-                                        uint32_t protocolVersion);
+    void
+    verifyArchivalOfCorruptedEntry(EvictedStateVectors const& evictedState,
+                                   ApplyLedgerStateSnapshot const& snapshot,
+                                   uint32_t ledgerSeq,
+                                   uint32_t protocolVersion);
     // Verifies that the batch of Hot Archive fixes on protocol 24 upgrade
     // corresponds to the expected data (i.e. only entries that were never
     // restored have been fixed, and that the fix comes back to the correct
@@ -171,7 +174,8 @@ class Protocol23CorruptionEventReconciler
 };
 
 void addHotArchiveBatchWithP23HotArchiveFix(
-    AbstractLedgerTxn& ltx, Application& app, LedgerHeader header,
+    AbstractLedgerTxn& ltx, Application& app,
+    ApplyLedgerStateSnapshot const& snapshot, LedgerHeader header,
     std::vector<LedgerEntry> const& archivedEntries,
     std::vector<LedgerKey> const& restoredEntries);
 
```

### src/main/QueryServer.cpp
```diff
@@ -87,8 +87,7 @@ QueryServer::QueryServer(std::string const& address, unsigned short port,
         auto workerPids = mServer.start();
         for (auto pid : workerPids)
         {
-            mSnapshots.emplace(pid,
-                               mAppConnector.copyLedgerStateSnapshot());
+            mSnapshots.emplace(pid, mAppConnector.copyLedgerStateSnapshot());
         }
     }
 }
```
