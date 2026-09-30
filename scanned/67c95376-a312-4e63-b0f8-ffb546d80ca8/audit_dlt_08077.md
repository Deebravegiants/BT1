# [?] init: [gui] Avoid UB/crash in InitAndLoadChainstate

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoin/bitcoin
Published: 2025-07-16
Source: https://github.com/bitcoin/bitcoin/commit/faaaddaaf8e5a63f19c4fc66aa79134987775f96
Type: security-commit

## Details
init: [gui] Avoid UB/crash in InitAndLoadChainstate

## Patch
### src/init.cpp
```diff
@@ -1224,13 +1224,24 @@ static ChainstateLoadResult InitAndLoadChainstate(
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
@@ -1259,6 +1270,7 @@ static ChainstateLoadResult InitAndLoadChainstate(
     // Creating the chainstate manager internally creates a BlockManager, opens
     // the blocks tree db, and wipes existing block files in case of a reindex.
     // The coinsdb is opened at a later point on LoadChainstate.
+    Assert(!node.chainman); // Was reset above
     try {
         node.chainman = std::make_unique<ChainstateManager>(*Assert(node.shutdown_signal), chainman_opts, blockman_opts);
     } catch (dbwrapper_error& e) {
@@ -1696,10 +1708,6 @@ bool AppInitMain(NodeContext& node, interfaces::BlockAndHeaderTipInfo* tip_info)
 
     // ********************************************************* Step 7: load block chain
 
-    node.notifications = std::make_unique<KernelNotifications>(Assert(node.shutdown_request), node.exit_status, *Assert(node.warnings));
-    auto& kernel_notifications{*node.notifications};
-    ReadNotificationArgs(args, kernel_notifications);
-
     // cache size calculations
     const auto [index_cache_sizes, kernel_cache_sizes] = CalculateCacheSizes(args, g_enabled_filter_types.size());
 
@@ -1759,6 +1767,7 @@ bool AppInitMain(NodeContext& node, interfaces::BlockAndHeaderTipInfo* tip_info)
     }
 
     ChainstateManager& chainman = *Assert(node.chainman);
+    auto& kernel_notifications{*Assert(node.notifications)};
 
     assert(!node.peerman);
     node.peerman = PeerManager::make(*node.connman, *node.addrman,
```
