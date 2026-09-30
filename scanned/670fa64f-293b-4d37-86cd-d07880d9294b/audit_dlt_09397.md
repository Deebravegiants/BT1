# [?] [mining] Fix potential crash bug in `submitblock`

## Summary
Severity: Unknown
Chain: Bitcoin Cash
Component: bitcoin-cash-node/bitcoin-cash-node
Published: 2021-08-02
Source: https://github.com/bitcoin-cash-node/bitcoin-cash-node/commit/6a8892b07d8dfdf168718ca82ac2ed1fbb370297
Type: security-commit

## Details
[mining] Fix potential crash bug in `submitblock`

## Patch
### src/bitcoind.cpp
```diff
@@ -22,6 +22,7 @@
 #include <util/strencodings.h>
 #include <util/system.h>
 #include <util/threadnames.h>
+#include <validationinterface.h>
 #include <walletinitinterface.h>
 
 #include <cstdio>
@@ -211,7 +212,9 @@ static bool AppInit(int argc, char *argv[]) {
     if (!fRet) {
         Interrupt();
     } else {
+        SetValidationInterfaceRegistrationsUnsafe(true);
         WaitForShutdown();
+        SetValidationInterfaceRegistrationsUnsafe(false);
     }
     Shutdown(node);
 
```

### src/init.cpp
```diff
@@ -38,6 +38,7 @@
 #include <policy/mempool.h>
 #include <policy/policy.h>
 #include <rpc/blockchain.h>
+#include <rpc/mining.h>
 #include <rpc/register.h>
 #include <rpc/server.h>
 #include <rpc/util.h>
@@ -312,6 +313,7 @@ void Shutdown(NodeContext &node) {
                   fsbridge::get_filesystem_error_message(e));
     }
     node.chain_clients.clear();
+    rpc::UnregisterSubmitBlockCatcher();
     UnregisterAllValidationInterfaces();
     GetMainSignals().UnregisterBackgroundSignalScheduler();
     GetMainSignals().UnregisterWithMempoolSignals(g_mempool);
@@ -2141,6 +2143,10 @@ bool AppInitMain(Config &config, RPCServer &rpcServer,
     // when load() and start() interface methods are called below.
     g_wallet_init_interface.Construct(node);
 
+    // Register the special submitblock state catcher validation interface before
+    // we start RPC
+    rpc::RegisterSubmitBlockCatcher();
+
     /**
      * Register RPC commands regardless of -server setting so they will be
      * available in the GUI RPC console even if external calls are disabled.
```

### src/rpc/mining.cpp
```diff
@@ -39,7 +39,10 @@
 #include <cstdint>
 #include <cstring>
 #include <list>
+#include <map>
 #include <memory>
+#include <utility>
+#include <vector>
 
 /**
  * Return average network hashes per second based on the last 'lookup' blocks,
@@ -887,27 +890,85 @@ static UniValue getblocktemplatelight(const Config &config, const JSONRPCRequest
     return getblocktemplatecommon(true, config, request);
 }
 
-class submitblock_StateCatcher : public CValidationInterface {
+namespace {
+struct submitblock_StateCatcher final : CValidationInterface, std::enable_shared_from_this<submitblock_StateCatcher> {
+    struct ReqEntry {
+        Mutex mut;
+        CValidationState state GUARDED_BY(mut);
+        bool found GUARDED_BY(mut) {false};
+    };
+
+private:
+    using Requests = std::multimap<BlockHash, std::weak_ptr<ReqEntry>>;
+    Mutex mut;
+    Requests requests GUARDED_BY(mut);
+
+    submitblock_StateCatcher() = default; // force user code to use Create() to construct instances
+
 public:
-    uint256 hash;
-    bool found;
-    CValidationState state;
+    // factory method to create a new instance
+    static std::shared_ptr<submitblock_StateCatcher> Create() {
+        // NB: we cannot make_shared here because of the private c'tor
+        return std::shared_ptr<submitblock_StateCatcher>(new submitblock_StateCatcher);
+    }
 
-    explicit submitblock_StateCatcher(const uint256 &hashIn)
-        : hash(hashIn), found(false), state() {}
+    // call this to "listen" for BlockChecked events on a block hash
+    std::shared_ptr<ReqEntry> AddRequest(const BlockHash &hash) {
+        LOCK(mut);
+        auto it = requests.emplace(std::piecewise_construct, std::forward_as_tuple(hash), std::forward_as_tuple());
+        std::shared_ptr<ReqEntry> ret(new ReqEntry, [weakSelf=weak_from_this(), it](ReqEntry *e){
+            // this deleter will auto-clean entry from the multimap when caller is done with the Request instance
+            if (auto self = weakSelf.lock()) {
+                LOCK(self->mut);
+                self->requests.erase(it);
+            }
+            delete e;
+        });
+        it->second = ret; // save weak_ptr ref
+        return ret;
+    }
 
-protected:
-    void BlockChecked(const CBlock &block,
-                      const CValidationState &stateIn) override {
-        if (block.GetHash() != hash) {
-            return;
+    // from CValidationInterface
+    void BlockChecked(const CBlock &block, const CValidationState &stateIn) override {
+        assert(!weak_from_this().expired());
+        std::vector<std::shared_ptr<ReqEntry>> matches;
+        {
+            LOCK(mut);
+            for (auto [it, end] = requests.equal_range(block.GetHash()); it != end; ++it) {
+                if (auto req = it->second.lock()) {
+                    matches.push_back(std::move(req));
+                }
+            }
+        }
+        for (const auto &req : matches) {
+            LOCK(req->mut);
+            req->state = stateIn;
+            req->found = true;
         }
-
-        found = true;
-        state = stateIn;
     }
 };
 
+std::shared_ptr<submitblock_StateCatcher> submitblock_Catcher;
+
+} // namespace
+
+namespace rpc {
+void RegisterSubmitBlockCatcher() {
+    if (submitblock_Catcher) {
+        LogPrintf("WARNING: %s called, but a valid submitblock_Catcher instance is already alive! FIXME!\n", __func__);
+        UnregisterSubmitBlockCatcher(); // kill current instance
+    }
+    submitblock_Catcher = submitblock_StateCatcher::Create();
+    RegisterValidationInterface(submitblock_Catcher.get());
+}
+void UnregisterSubmitBlockCatcher() {
+    if (submitblock_Catcher) {
+        UnregisterValidationInterface(submitblock_Catcher.get());
+        submitblock_Catcher.reset();
+    }
+}
+} // namespace rpc
+
 /// If jobId is not nullptr, we are in `submitblocklight` mode, otherwise we are in regular `submitblock` mode.
 static UniValue submitblockcommon(const Config &config, const JSONRPCRequest &request,
                                   const gbtl::JobId *jobId = nullptr) {
@@ -954,30 +1015,32 @@ static UniValue submitblockcommon(const Config &config, const JSONRPCRequest &re
         }
     }
 
+    if (!submitblock_Catcher) {
+        // The catcher has not yet been initialized -- this should never happen under normal circumstances but
+        // in case some tests or benches neglect to initialize, we check for this.
+        throw JSONRPCError(RPC_IN_WARMUP, "The submitblock subsystem has not yet been fully started.");
+    }
+    const auto sc_req = submitblock_Catcher->AddRequest(block.GetHash());
     bool new_block;
-    submitblock_StateCatcher sc(block.GetHash());
-    RegisterValidationInterface(&sc);
-    bool accepted =
-        ProcessNewBlock(config, blockptr, /* fForceProcessing */ true, /* fNewBlock */ &new_block);
-    // We are only interested in BlockChecked which will have been dispatched
-    // in-thread, so no need to sync before unregistering.
-    UnregisterValidationInterface(&sc);
-    // Sync to ensure that the catcher's slots aren't executing when it goes out
-    // of scope and is deleted.
-    SyncWithValidationInterfaceQueue();
+    const bool accepted = ProcessNewBlock(config, blockptr, /* fForceProcessing */ true, /* fNewBlock */ &new_block);
+    // Note: We are only interested in BlockChecked which will have been dispatched in-thread before ProcessnewBlock
+    //       returns.
+
     if (!new_block && accepted) {
         return "duplicate";
     }
 
-    if (!sc.found) {
+    LOCK(sc_req->mut);
+    if (!sc_req->found) {
         return "inconclusive";
     }
+    auto result = BIP22ValidationResult(config, sc_req->state);
 
-    auto result = BIP22ValidationResult(config, sc.state);
     if (jobId) {
         LogPrint(BCLog::RPC, "SubmitBlock (light) deserialize duration: %f seconds\n", tDeserTx / 1e6);
     }
     LogPrint(BCLog::RPC, "SubmitBlock total duration: %f seconds\n", (GetTimeMicros() - t0) / 1e6);
+
     return result;
 }
 
```

### src/rpc/mining.h
```diff
@@ -1,4 +1,5 @@
 // Copyright (c) 2017 The Bitcoin Core developers
+// Copyright (c) 2021 The Bitcoin developers
 // Distributed under the MIT software license, see the accompanying
 // file COPYING or http://www.opensource.org/licenses/mit-license.php.
 
@@ -21,6 +22,13 @@ UniValue generateBlocks(const Config &config,
                         std::shared_ptr<CReserveScript> coinbaseScript,
                         int nGenerate, uint64_t nMaxTries, bool keepScript);
 
+namespace rpc {
+/** Called by init code to register the internal "submitblock_StateCatcher" class. */
+void RegisterSubmitBlockCatcher();
+/** Called by shutdown code to delete the internal "submitblock_StateCatcher" class. */
+void UnregisterSubmitBlockCatcher();
+} // namespace rpc
+
 namespace gbtl {
 /** Used by getblocktemplatelight for the "merkle" UniValue entry it returns.  Returns a merkle branch used to
  *  reconstruct the merkle root for submitblocklight.  See the implementation of this function for more documentation.*/
```

### src/test/rpc_tests.cpp
```diff
@@ -23,6 +23,10 @@
 
 #include <rpc/blockchain.h>
 
+#include <array>
+#include <thread>
+#include <vector>
+
 UniValue CallRPC(const std::string &args)
 {
     std::vector<std::string> vArgs;
@@ -569,4 +573,42 @@ BOOST_AUTO_TEST_CASE(rpc_getblockstats_calculate_percentiles_by_size)
     }
 }
 
+BOOST_AUTO_TEST_CASE(rpc_submitblock_parallel) {
+    /* This test ensures that submitblock has no regressions after partially fixing issue #149, and that it supports
+     * receiving blocks in parallel without crashing. */
+    static constexpr size_t n_threads = 4, n_iters_per_thread = 100;
+    const std::array<std::string, 2> dummy_blocks_hex = {{
+        "00000020ba9483ce1345d9b51538a47c84ca69a2f374428f79a2fa29cfeb406b000000001884a0413e9f76b0560"
+        "5ccbefc4b6be0024dfa86d3767f9777bd2cfe65c30bd858a4445fffff001d9f4528e20101000000010000000000"
+        "000000000000000000000000000000000000000000000000000000ffffffff2e02300600fec3121900fe78ca070"
+        "00963676d696e657234320800000000000000000b2f636865636b73756d302f00ffffffff0100f2052a01000000"
+        "1976a91477f70060b91e3f5a89b6de3531a580c8494605e988ac00000000",
+        "00000020ff1e59f17554af4fef82141c0fd9034f74d44f9f06957bcfac362723000000001a4245e03250e70dee6"
+        "503ee8daf6b81a6807e330394265a022cc2b8ba81a4ad2cf0c860ffff001da8aa3c1f0101000000010000000000"
+        "000000000000000000000000000000000000000000000000000000ffffffff48037728160c0b2f454233322f414"
+        "431322f042cf0c86004ed6201250c0d979b604e050000000000000a626368706f6f6c172f20626974636f696e63"
+        "6173682e6e6574776f726b202fffffffff01c817a804000000001976a914158b5d181552c9f4f267c0de68aae49"
+        "63043993988ac00000000",
+    }};
+    std::vector<std::vector<UniValue>> results(n_threads);
+    std::vector<std::thread> threads;
+    for (size_t i = 0; i < n_threads; ++i) {
+        threads.emplace_back([&hex = dummy_blocks_hex[i % dummy_blocks_hex.size()], &res = results[i]]{
+             for (size_t j = 0; j < n_iters_per_thread; ++j) {
+                 // push results -- we do this to avoid doing unsafe BOOST_CHECK_EQUAL in a thread
+                 res.push_back(CallRPC("submitblock " + hex));
+             }
+        });
+    }
+    for (auto & thr : threads)
+        thr.join();
+    // ensure all results match what we expect; these are real blocks from testnet3 and testnet4, so they will have
+    // gone through basic checks and thus our submitblock_StateCatcher should have been invoked.
+    for (const auto &res : results) {
+        for (const auto &unival : res) {
+            BOOST_CHECK_EQUAL(unival.get_str(), "prev-blk-not-found");
+        }
+    }
+}
+
 BOOST_AUTO_TEST_SUITE_END()
```

### src/test/setup_common.cpp
```diff
@@ -20,6 +20,7 @@
 #include <pow.h>
 #include <pubkey.h>
 #include <random.h>
+#include <rpc/mining.h>
 #include <rpc/register.h>
 #include <rpc/server.h>
 #include <script/script_error.h>
@@ -106,6 +107,7 @@ TestingSetup::TestingSetup(const std::string &chainName)
     // from blocking due to queue overrun.
     threadGroup.create_thread(std::bind(&CScheduler::serviceQueue, &scheduler));
     GetMainSignals().RegisterBackgroundSignalScheduler(scheduler);
+    rpc::RegisterSubmitBlockCatcher();
 
     g_mempool.setSanityCheck(1.0);
     pblocktree.reset(new CBlockTreeDB(1 << 20, true));
@@ -138,6 +140,7 @@ TestingSetup::~TestingSetup() {
     threadGroup.join_all();
     StopScriptCheckWorkerThreads();
     GetMainSignals().FlushBackgroundCallbacks();
+    rpc::UnregisterSubmitBlockCatcher();
     GetMainSignals().UnregisterBackgroundSignalScheduler();
     g_connman.reset();
     g_banman.reset();
```

### src/validationinterface.cpp
```diff
@@ -117,7 +117,19 @@ CMainSignals &GetMainSignals() {
     return g_signals;
 }
 
+static std::atomic_bool g_reg_unsafe{false};
+
+void SetValidationInterfaceRegistrationsUnsafe(bool unsafe) { g_reg_unsafe = unsafe; }
+
+static void LogIfUnsafe(const char *func) {
+    if (g_reg_unsafe) {
+        LogPrintf("WARNING: %s called from outside of the init/shutdown code paths (thread: %s)."
+                  " This is not supported! FIXME!\n", func, util::ThreadGetInternalName());
+    }
+}
+
 void RegisterValidationInterface(CValidationInterface *pwalletIn) {
+    LogIfUnsafe(__func__);
     ValidationInterfaceConnections &conns =
         g_signals.m_internals->m_connMainSignals[pwalletIn];
     conns.UpdatedBlockTip = g_signals.m_internals->UpdatedBlockTip.connect(
@@ -163,6 +175,7 @@ void RegisterValidationInterface(CValidationInterface *pwalletIn) {
 
 void UnregisterValidationInterface(CValidationInterface *pwalletIn) {
     if (g_signals.m_internals) {
+        LogIfUnsafe(__func__);
         g_signals.m_internals->m_connMainSignals.erase(pwalletIn);
     }
 }
@@ -171,6 +184,7 @@ void UnregisterAllValidationInterfaces() {
     if (!g_signals.m_internals) {
         return;
     }
+    LogIfUnsafe(__func__);
     g_signals.m_internals->m_connMainSignals.clear();
 }
 
```

### src/validationinterface.h
```diff
@@ -31,12 +31,28 @@ enum class MemPoolRemovalReason;
 
 // These functions dispatch to one or all registered wallets
 
-/** Register a wallet to receive updates from core */
+/**
+ *  Register a wallet to receive updates from core.
+ *  WARNING: Do not call this after the app has initialized and threads are started.  It is not thread-safe.
+ */
 void RegisterValidationInterface(CValidationInterface *pwalletIn);
-/** Unregister a wallet from core */
+/**
+ *  Unregister a wallet from core.
+ *  WARNING: Do not call this after the app has initialized and threads are started.  It is not thread-safe.
+ *           It may, however, be called by the "shutdown" code.
+ */
 void UnregisterValidationInterface(CValidationInterface *pwalletIn);
-/** Unregister all wallets from core */
+/**
+ *  Unregister all wallets from core
+ *  WARNING: Do not call this after the app has initialized and threads are started.  It is not thread-safe.
+ *           It may, however, be called by the "shutdown" code.
+ */
 void UnregisterAllValidationInterfaces();
+/**
+ *  Called from the init process to indicate that future calls to Register/UnregisterValidationInterface()
+ *  are no longer safe (this is for debug log purposes only).
+ */
+void SetValidationInterfaceRegistrationsUnsafe(bool unsafe);
 /**
  * Pushes a function to callback onto the notification queue, guaranteeing any
  * callbacks generated prior to now are finished when the function is called.
```
