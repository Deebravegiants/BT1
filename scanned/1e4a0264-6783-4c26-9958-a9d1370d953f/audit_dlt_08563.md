# [?] Fix tmpdir-reuse crash bug of new QIC

## Summary
Severity: Unknown
Chain: Stellar
Component: stellar/stellar-core
Published: 2025-07-08
Source: https://github.com/stellar/stellar-core/commit/a2163aded8efab4cbc7a6600b8a4ecbf9ca0bfd5
Type: security-commit

## Details
Fix tmpdir-reuse crash bug of new QIC

## Patch
### src/herder/HerderImpl.cpp
```diff
@@ -99,8 +99,7 @@ HerderImpl::HerderImpl(Application& app)
     , mLedgerManager(app.getLedgerManager())
     , mSCPMetrics(app)
     , mLastQuorumMapIntersectionState(
-          std::make_shared<QuorumMapIntersectionState>(
-              app.getTmpDirManager().tmpDir("herder-qic"), app.getMetrics()))
+          std::make_shared<QuorumMapIntersectionState>(app))
     , mState(Herder::HERDER_BOOTING_STATE)
 {
     auto ln = getSCP().getLocalNode();
@@ -1916,10 +1915,11 @@ HerderImpl::checkAndMaybeReanalyzeQuorumMapV2()
 
     CLOG_INFO(Herder,
               "Transitive closure of quorum has changed, re-analyzing.");
+    mLastQuorumMapIntersectionState->reset(mApp);
     mLastQuorumMapIntersectionState->mRecalculating = true;
     mLastQuorumMapIntersectionState->mCheckingQuorumMapHash = curr;
     quorum_checker::runQuorumIntersectionCheckAsync(
-        curr, trackingConsensusLedgerIndex(),
+        mApp, curr, trackingConsensusLedgerIndex(),
         mLastQuorumMapIntersectionState->mTmpDir->getName(), qmap,
         mLastQuorumMapIntersectionState, mApp.getProcessManager(),
         mApp.getConfig().QUORUM_INTERSECTION_CHECKER_TIME_LIMIT_MS,
@@ -1979,9 +1979,9 @@ HerderImpl::checkAndMaybeReanalyzeQuorumMap()
 
         auto ledger = trackingConsensusLedgerIndex();
         auto nNodes = qmap.size();
-        auto& hState = mLastQuorumMapIntersectionState;
+        auto hState = mLastQuorumMapIntersectionState;
         auto& app = mApp;
-        auto worker = [curr, ledger, nNodes, qmap, cfg, seed, &app, &hState] {
+        auto worker = [curr, ledger, nNodes, qmap, cfg, seed, &app, hState] {
             try
             {
                 ZoneScoped;
@@ -2011,13 +2011,12 @@ HerderImpl::checkAndMaybeReanalyzeQuorumMap()
                             toQuorumIntersectionMap(qmap), cfg, cb);
                 }
                 app.postOnMainThread(
-                    [ok, curr, ledger, nNodes, split, critical, &hState] {
-                        hState->mRecalculating = false;
-                        hState->mInterruptFlag = false;
+                    [ok, curr, ledger, nNodes, split, critical, hState, &app] {
+                        hState->reset(app);
+
                         hState->mNumNodes = nNodes;
                         hState->mLastCheckLedger = ledger;
                         hState->mLastCheckQuorumMapHash = curr;
-                        hState->mCheckingQuorumMapHash = Hash{};
                         hState->mPotentialSplit = split;
                         hState->mIntersectionCriticalNodes = critical;
                         if (ok)
@@ -2031,27 +2030,17 @@ HerderImpl::checkAndMaybeReanalyzeQuorumMap()
             {
                 CLOG_DEBUG(Herder,
                            "Quorum transitive closure analysis interrupted.");
-                app.postOnMainThread(
-                    [&hState] {
-                        hState->mRecalculating = false;
-                        hState->mInterruptFlag = false;
-                        hState->mCheckingQuorumMapHash = Hash{};
-                    },
-                    "QuorumIntersectionChecker interrupted");
+                app.postOnMainThread([hState, &app] { hState->reset(app); },
+                                     "QuorumIntersectionChecker interrupted");
             }
             catch (const RustQuorumCheckerError& e)
             {
                 CLOG_DEBUG(Herder,
                            "Quorum transitive closure analysis failed due to "
                            "Rust solver error: {}",
                            e.what());
-                app.postOnMainThread(
-                    [&hState] {
-                        hState->mRecalculating = false;
-                        hState->mInterruptFlag = false;
-                        hState->mCheckingQuorumMapHash = Hash{};
-                    },
-                    "QuorumIntersectionChecker rust error");
+                app.postOnMainThread([hState, &app] { hState->reset(app); },
+                                     "QuorumIntersectionChecker rust error");
             }
         };
         mApp.postOnBackgroundThread(worker, "QuorumIntersectionChecker");
```

### src/herder/QuorumIntersectionChecker.h
```diff
@@ -55,12 +55,8 @@ struct QuorumMapIntersectionState
         return mLastCheckLedger == mLastGoodLedger;
     }
 
-    QuorumMapIntersectionState(TmpDir&& tmpDir,
-                               medida::MetricsRegistry& metrics)
-        : mTmpDir(std::make_unique<TmpDir>(std::move(tmpDir)))
-        , mMetrics(metrics)
-    {
-    }
+    void reset(Application& app);
+    QuorumMapIntersectionState(Application& app);
 };
 
 class QuorumIntersectionChecker
```

### src/herder/QuorumIntersectionCheckerImpl.cpp
```diff
@@ -6,6 +6,7 @@
 #include "QuorumIntersectionChecker.h"
 #include "herder/HerderUtils.h"
 
+#include "main/Application.h"
 #include "util/GlobalChecks.h"
 #include "util/Logging.h"
 #include "util/Math.h"
@@ -790,6 +791,24 @@ groupString(std::optional<Config> const& cfg, std::set<NodeID> const& group)
 
 namespace stellar
 {
+
+void
+QuorumMapIntersectionState::reset(Application& app)
+{
+    // NB: this deletes any existing tmp dir before creating a new one.
+    mTmpDir =
+        std::make_unique<TmpDir>(app.getTmpDirManager().tmpDir("qic-tmp"));
+    mRecalculating = false;
+    mInterruptFlag = false;
+    mCheckingQuorumMapHash = Hash{};
+}
+
+QuorumMapIntersectionState::QuorumMapIntersectionState(Application& app)
+    : mMetrics(app.getMetrics())
+{
+    reset(app);
+}
+
 std::shared_ptr<QuorumIntersectionChecker>
 QuorumIntersectionChecker::create(
     QuorumTracker::QuorumMap const& qmap, std::optional<Config> const& cfg,
```

### src/herder/RustQuorumCheckerAdaptor.cpp
```diff
@@ -470,8 +470,8 @@ networkEnjoysQuorumIntersection(std::string const& inJsonPath,
 
 void
 runQuorumIntersectionCheckAsync(
-    Hash const curr, uint32 ledger, std::string const& tmpDirName,
-    QuorumTracker::QuorumMap const& qmap,
+    Application& app, Hash const curr, uint32 ledger,
+    std::string const& tmpDirName, QuorumTracker::QuorumMap const& qmap,
     std::weak_ptr<QuorumMapIntersectionState> hState, ProcessManager& pm,
     uint64_t timeLimitMs, size_t memoryLimitBytes, bool analyzeCriticalGroups)
 {
@@ -501,8 +501,19 @@ runQuorumIntersectionCheckAsync(
         analyzeCriticalGroups ? "--analyze-critical-groups" : "");
     auto evt = pm.runProcess(cmdline, qicOutFile).lock();
 
-    evt->async_wait([numNodes, ledger, curr, qicOutFile, qicResultJson,
-                     hState](asio::error_code ec) {
+    if (!evt)
+    {
+        CLOG_ERROR(SCP, "Failed to start quorum intersection check process");
+        auto hStateSP = hState.lock();
+        if (hStateSP)
+        {
+            hStateSP->reset(app);
+        }
+        return;
+    }
+
+    evt->async_wait([numNodes, ledger, curr, qicOutFile, qicResultJson, hState,
+                     &app](asio::error_code ec) {
         auto hStateSP = hState.lock();
         if (hStateSP == nullptr)
         {
@@ -565,8 +576,7 @@ runQuorumIntersectionCheckAsync(
             CLOG_ERROR(SCP, "quorum intersection command failed, rc = {}",
                        ecode);
         }
-        hStateSP->mRecalculating = false;
-        hStateSP->mCheckingQuorumMapHash = Hash{};
+        hStateSP->reset(app);
     });
 }
 
```

### src/herder/RustQuorumCheckerAdaptor.h
```diff
@@ -79,8 +79,8 @@ QuorumCheckerStatus networkEnjoysQuorumIntersection(
 // analysis. Results are read from the output JSON file and propagated back to
 // the main process through the provided QuorumMapIntersectionState.
 void runQuorumIntersectionCheckAsync(
-    Hash const curr, uint32 ledger, std::string const& tmpDirName,
-    QuorumTracker::QuorumMap const& qmap,
+    Application& app, Hash const curr, uint32 ledger,
+    std::string const& tmpDirName, QuorumTracker::QuorumMap const& qmap,
     std::weak_ptr<QuorumMapIntersectionState> hState, ProcessManager& pm,
     uint64_t timeLimitMs, size_t memoryLimitBytes, bool analyzeCriticalGroups);
 
```

### src/herder/test/QuorumIntersectionTests.cpp
```diff
@@ -30,7 +30,7 @@ using std::make_shared;
 
 void
 quorumIntersectionCheckerV2Wrapper(
-    std::shared_ptr<QuorumMapIntersectionState> const& state,
+    Application& app, std::shared_ptr<QuorumMapIntersectionState> const& state,
     QuorumTracker::QuorumMap const& qmap, ProcessManager& pm,
     VirtualClock& clock, bool analyzeCriticalGroups, uint32_t timeLimit,
     uint32_t memoryLimit)
@@ -50,7 +50,7 @@ quorumIntersectionCheckerV2Wrapper(
     auto resultPotentialSplitCountBefore = resultPotentialSplitCounter.count();
 
     quorum_checker::runQuorumIntersectionCheckAsync(
-        curr, testLedgerNo, state->mTmpDir->getName(), qmap, state, pm,
+        app, curr, testLedgerNo, state->mTmpDir->getName(), qmap, state, pm,
         timeLimit, memoryLimit, analyzeCriticalGroups);
 
     while (state->mRecalculating && !clock.getIOContext().stopped())
@@ -101,11 +101,10 @@ networkEnjoysQuorumIntersectionV2Wrapper(QuorumTracker::QuorumMap const& qmap,
 {
     VirtualClock clock;
     Application::pointer app = createTestApplication(clock, cfg);
-    auto state = std::make_shared<QuorumMapIntersectionState>(
-        app->getTmpDirManager().tmpDir("qic-test"), app->getMetrics());
+    auto state = std::make_shared<QuorumMapIntersectionState>(*app);
     state->mRecalculating = true;
     quorumIntersectionCheckerV2Wrapper(
-        state, qmap, app->getProcessManager(), clock, false,
+        *app, state, qmap, app->getProcessManager(), clock, false,
         cfg.QUORUM_INTERSECTION_CHECKER_TIME_LIMIT_MS,
         cfg.QUORUM_INTERSECTION_CHECKER_MEMORY_LIMIT_BYTES);
     return state->mStatus == QuorumCheckerStatus::UNSAT;
@@ -117,11 +116,10 @@ runIntersectionCriticalGroupsCheckV2(QuorumTracker::QuorumMap const& qmap,
 {
     VirtualClock clock;
     Application::pointer app = createTestApplication(clock, cfg);
-    auto state = std::make_shared<QuorumMapIntersectionState>(
-        app->getTmpDirManager().tmpDir("qic-test"), app->getMetrics());
+    auto state = std::make_shared<QuorumMapIntersectionState>(*app);
     state->mRecalculating = true;
     quorumIntersectionCheckerV2Wrapper(
-        state, qmap, app->getProcessManager(), clock, true,
+        *app, state, qmap, app->getProcessManager(), clock, true,
         cfg.QUORUM_INTERSECTION_CHECKER_TIME_LIMIT_MS,
         cfg.QUORUM_INTERSECTION_CHECKER_MEMORY_LIMIT_BYTES);
     return state->mIntersectionCriticalNodes;
@@ -143,6 +141,44 @@ runIntersectionCriticalGroupsCheck(QuorumTracker::QuorumMap const& initQmap,
         toQuorumIntersectionMap(initQmap), config, qic);
 }
 
+TEST_CASE("new QIC on same app run multiple times in a row",
+          "[herder][quorumintersection]")
+{
+    QuorumTracker::QuorumMap qm;
+
+    PublicKey pkA = SecretKey::pseudoRandomForTesting().getPublicKey();
+    PublicKey pkB = SecretKey::pseudoRandomForTesting().getPublicKey();
+    PublicKey pkC = SecretKey::pseudoRandomForTesting().getPublicKey();
+    PublicKey pkD = SecretKey::pseudoRandomForTesting().getPublicKey();
+
+    qm[pkA] = QuorumTracker::NodeInfo{
+        make_shared<QS>(2, VK({pkB, pkC, pkD}), VQ{}), 0};
+    qm[pkB] = QuorumTracker::NodeInfo{
+        make_shared<QS>(2, VK({pkA, pkC, pkD}), VQ{}), 0};
+    qm[pkC] = QuorumTracker::NodeInfo{
+        make_shared<QS>(2, VK({pkA, pkB, pkD}), VQ{}), 0};
+    qm[pkD] = QuorumTracker::NodeInfo{
+        make_shared<QS>(2, VK({pkA, pkB, pkC}), VQ{}), 0};
+
+    Config cfg(getTestConfig());
+
+    VirtualClock clock;
+    Application::pointer app = createTestApplication(clock, cfg);
+    auto state = std::make_shared<QuorumMapIntersectionState>(*app);
+    for (int i = 0; i < 10; ++i)
+    {
+        // reset state before each run
+        state->reset(*app);
+        state->mRecalculating = true;
+        state->mStatus = QuorumCheckerStatus::UNKNOWN;
+        quorumIntersectionCheckerV2Wrapper(
+            *app, state, qm, app->getProcessManager(), clock, false,
+            cfg.QUORUM_INTERSECTION_CHECKER_TIME_LIMIT_MS,
+            cfg.QUORUM_INTERSECTION_CHECKER_MEMORY_LIMIT_BYTES);
+        REQUIRE(state->mStatus == QuorumCheckerStatus::UNSAT);
+    }
+}
+
 TEST_CASE("quorum intersection basic 4-node", "[herder][quorumintersection]")
 {
     QuorumTracker::QuorumMap qm;
```
