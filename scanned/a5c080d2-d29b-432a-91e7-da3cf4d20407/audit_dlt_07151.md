# [?] Merge bitcoin/bitcoin#32987: init: [gui] Avoid UB/crash in InitAndLoadChainstate

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoin/bitcoin
Published: 2025-07-30
Source: https://github.com/bitcoin/bitcoin/commit/547c64814d07b992a4779b8a9cf08232554d86ed
Type: security-commit

## Details
Merge bitcoin/bitcoin#32987: init: [gui] Avoid UB/crash in InitAndLoadChainstate

fac90e5261b811739ada56e06ea793a12f9c2c3d test: Check that the GUI interactive reindex works (MarcoFalke)
faaaddaaf8e5a63f19c4fc66aa79134987775f96 init: [gui] Avoid UB/crash in InitAndLoadChainstate (MarcoFalke)

Pull request description:

  `InitAndLoadChainstate` is problematic, when called twice in the GUI. This can happen when it returns a failure and the user selects an interactive reindex.

  There are several bugs that have been introduced since the last time this was working correctly:

  * The first one is a crash (assertion failure), which happens due to a cached tip block in the notifiications from the previous run. See https://github.com/bitcoin/bitcoin/pull/31346#discussion_r2207914726
  * The second one is UB (use-after-free), which happens because the block index db in the blockmanager is not reset. See https://github.com/bitcoin/bitcoin/pull/30965#discussion_r2207822121

  Fix both bugs by resetting any dirty state in `InitAndLoadChainstate`.

  Also, add a test, because I don't really want to keep testing this manually every time. (A failing test run can be seen in https://github.com/bitcoin/bitcoin/pull/32979/checks)

ACKs for top commit:
  achow101:
    ACK fac90e5261b811739ada56e06ea793a12f9c2c3d
  TheCharlatan:
    ACK fac90e5261b811739ada56e06ea793a12f9c2c3d
  mzumsande:
    Tested ACK fac90e5261b811739ada56e06ea793a12f9c2c3d

Tree-SHA512: 9f744d36e7cdd3f5871764386ec5a5cca1ae144f1bacc26c07e60313c2bdacdc5fca351aa185cb51359540eea4534dda17e4fb6073ad90f91ba0a6936faeead8

## Patch
### src/common/args.cpp
```diff
@@ -709,6 +709,7 @@ std::string HelpMessageOpt(const std::string &option, const std::string &message
 
 const std::vector<std::string> TEST_OPTIONS_DOC{
     "addrman (use deterministic addrman)",
+    "reindex_after_failure_noninteractive_yes (When asked for a reindex after failure interactively, simulate as-if answered with 'yes')",
     "bip94 (enforce BIP94 consensus rules)",
 };
 
```

### src/init.cpp
```diff
@@ -1223,13 +1223,24 @@ static ChainstateLoadResult InitAndLoadChainstate(
     const kernel::CacheSizes& cache_sizes,
     const ArgsManager& args)
 {
+    // This function may be called twice, so any dirty state must be reset.
+    node.notifications.reset(); // Drop state, such as a cached tip block
+    node.mempool.reset();
+    node.chainman.reset(); // Drop state, such as an initialized m_block_tree_db
+
     const CChainParams& chainparams = Params();
+
+    Assert(!node.notifications); // Was reset above
+    node.notifications = std::make_unique<KernelNotifications>(Assert(node.shutdown_request), node.exit_status, *Assert(node.warnings));
+    ReadNotificationArgs(args, *node.notifications);
+
     CTxMemPool::Options mempool_opts{
         .check_ratio = chainparams.DefaultConsistencyChecks() ? 1 : 0,
         .signals = node.validation_signals.get(),
     };
     Assert(ApplyArgsManOptions(args, chainparams, mempool_opts)); // no error can happen, already checked in AppInitParameterInteraction
     bilingual_str mempool_error;
+    Assert(!node.mempool); // Was reset above
     node.mempool = std::make_unique<CTxMemPool>(mempool_opts, mempool_error);
     if (!mempool_error.empty()) {
         return {ChainstateLoadStatus::FAILURE_FATAL, mempool_error};
@@ -1260,6 +1271,7 @@ static ChainstateLoadResult InitAndLoadChainstate(
     // Creating the chainstate manager internally creates a BlockManager, opens
     // the blocks tree db, and wipes existing block files in case of a reindex.
     // The coinsdb is opened at a later point on LoadChainstate.
+    Assert(!node.chainman); // Was reset above
     try {
         node.chainman = std::make_unique<ChainstateManager>(*Assert(node.shutdown_signal), chainman_opts, blockman_opts);
     } catch (dbwrapper_error& e) {
@@ -1697,10 +1709,6 @@ bool AppInitMain(NodeContext& node, interfaces::BlockAndHeaderTipInfo* tip_info)
 
     // ********************************************************* Step 7: load block chain
 
-    node.notifications = std::make_unique<KernelNotifications>(Assert(node.shutdown_request), node.exit_status, *Assert(node.warnings));
-    auto& kernel_notifications{*node.notifications};
-    ReadNotificationArgs(args, kernel_notifications);
-
     // cache size calculations
     const auto [index_cache_sizes, kernel_cache_sizes] = CalculateCacheSizes(args, g_enabled_filter_types.size());
 
@@ -1730,10 +1738,11 @@ bool AppInitMain(NodeContext& node, interfaces::BlockAndHeaderTipInfo* tip_info)
         args);
     if (status == ChainstateLoadStatus::FAILURE && !do_reindex && !ShutdownRequested(node)) {
         // suggest a reindex
-        bool do_retry = uiInterface.ThreadSafeQuestion(
+        bool do_retry{HasTestOption(args, "reindex_after_failure_noninteractive_yes") ||
+            uiInterface.ThreadSafeQuestion(
             error + Untranslated(".\n\n") + _("Do you want to rebuild the databases now?"),
             error.original + ".\nPlease restart with -reindex or -reindex-chainstate to recover.",
-            "", CClientUIInterface::MSG_ERROR | CClientUIInterface::BTN_ABORT);
+            "", CClientUIInterface::MSG_ERROR | CClientUIInterface::BTN_ABORT)};
         if (!do_retry) {
             return false;
         }
@@ -1760,6 +1769,7 @@ bool AppInitMain(NodeContext& node, interfaces::BlockAndHeaderTipInfo* tip_info)
     }
 
     ChainstateManager& chainman = *Assert(node.chainman);
+    auto& kernel_notifications{*Assert(node.notifications)};
 
     assert(!node.peerman);
     node.peerman = PeerManager::make(*node.connman, *node.addrman,
```

### test/functional/feature_reindex_init.py
```diff
@@ -0,0 +1,34 @@
+#!/usr/bin/env python3
+# Copyright (c) The Bitcoin Core developers
+# Distributed under the MIT software license, see the accompanying
+# file COPYING or http://www.opensource.org/licenses/mit-license.php.
+"""Test reindex works on init after a db load failure"""
+
+from test_framework.test_framework import BitcoinTestFramework
+from test_framework.util import assert_equal
+import os
+import shutil
+
+
+class ReindexInitTest(BitcoinTestFramework):
+    def set_test_params(self):
+        self.num_nodes = 1
+
+    def run_test(self):
+        node = self.nodes[0]
+        self.stop_nodes()
+
+        self.log.info("Removing the block index leads to init error")
+        shutil.rmtree(node.blocks_path / "index")
+        node.assert_start_raises_init_error(
+            expected_msg=f": Error initializing block database.{os.linesep}"
+            "Please restart with -reindex or -reindex-chainstate to recover.",
+        )
+
+        self.log.info("Allowing the reindex should work fine")
+        self.start_node(0, extra_args=["-test=reindex_after_failure_noninteractive_yes"])
+        assert_equal(node.getblockcount(), 200)
+
+
+if __name__ == "__main__":
+    ReindexInitTest(__file__).main()
```

### test/functional/test_runner.py
```diff
@@ -289,6 +289,7 @@
     'p2p_leak.py',
     'wallet_encryption.py',
     'feature_dersig.py',
+    'feature_reindex_init.py',
     'feature_cltv.py',
     'rpc_uptime.py',
     'feature_discover.py',
```
