# [?] fuzz: Avoid non-determinism in process_message(s) target (PeerMan)

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoin/bitcoin
Published: 2025-06-27
Source: https://github.com/bitcoin/bitcoin/commit/fa11eea4059a608f591db4469c07a341fd33a031
Type: security-commit

## Details
fuzz: Avoid non-determinism in process_message(s) target (PeerMan)

The PeerManager has several members, such as the FastRandomContext,
which need to be reset before every run to avoid leaking state from one
run into the next.

Also, style fixups in p2p_handshake.cpp, where this code is copied from.

## Patch
### src/test/fuzz/p2p_handshake.cpp
```diff
@@ -42,14 +42,14 @@ FUZZ_TARGET(p2p_handshake, .init = ::initialize)
     SeedRandomStateForTest(SeedRand::ZEROS);
     FuzzedDataProvider fuzzed_data_provider(buffer.data(), buffer.size());
 
-    ConnmanTestMsg& connman = static_cast<ConnmanTestMsg&>(*g_setup->m_node.connman);
+    auto& connman = static_cast<ConnmanTestMsg&>(*g_setup->m_node.connman);
     auto& chainman = static_cast<TestChainstateManager&>(*g_setup->m_node.chainman);
     SetMockTime(1610000000); // any time to successfully reset ibd
     chainman.ResetIbd();
 
     node::Warnings warnings{};
     NetGroupManager netgroupman{{}};
-    AddrMan addrman{netgroupman, /*deterministic=*/true, 0};
+    AddrMan addrman{netgroupman, /*deterministic=*/true, /*consistency_check_ratio=*/0};
     auto peerman = PeerManager::make(connman, addrman,
                                      /*banman=*/nullptr, chainman,
                                      *g_setup->m_node.mempool, warnings,
```

### src/test/fuzz/process_message.cpp
```diff
@@ -5,6 +5,7 @@
 #include <consensus/consensus.h>
 #include <net.h>
 #include <net_processing.h>
+#include <node/warnings.h>
 #include <primitives/transaction.h>
 #include <protocol.h>
 #include <script/script.h>
@@ -40,9 +41,11 @@ void initialize_process_message()
         Assert(std::count(ALL_NET_MESSAGE_TYPES.begin(), ALL_NET_MESSAGE_TYPES.end(), LIMIT_TO_MESSAGE_TYPE)); // Unknown message type passed
     }
 
-    static const auto testing_setup = MakeNoLogFileContext<const TestingSetup>(
+    static const auto testing_setup{
+        MakeNoLogFileContext<TestingSetup>(
             /*chain_type=*/ChainType::REGTEST,
-            {.extra_args = {"-txreconciliation"}});
+            {}),
+    };
     g_setup = testing_setup.get();
     SetMockTime(WITH_LOCK(g_setup->m_node.chainman->GetMutex(), return g_setup->m_node.chainman->ActiveTip()->Time()));
     for (int i = 0; i < 2 * COINBASE_MATURITY; i++) {
@@ -56,11 +59,23 @@ FUZZ_TARGET(process_message, .init = initialize_process_message)
     SeedRandomStateForTest(SeedRand::ZEROS);
     FuzzedDataProvider fuzzed_data_provider(buffer.data(), buffer.size());
 
-    ConnmanTestMsg& connman = *static_cast<ConnmanTestMsg*>(g_setup->m_node.connman.get());
+    auto& connman = static_cast<ConnmanTestMsg&>(*g_setup->m_node.connman);
     auto& chainman = static_cast<TestChainstateManager&>(*g_setup->m_node.chainman);
     SetMockTime(1610000000); // any time to successfully reset ibd
     chainman.ResetIbd();
 
+    node::Warnings warnings{};
+    NetGroupManager netgroupman{{}};
+    AddrMan addrman{netgroupman, /*deterministic=*/true, /*consistency_check_ratio=*/0};
+    auto peerman = PeerManager::make(connman, addrman,
+                                     /*banman=*/nullptr, chainman,
+                                     *g_setup->m_node.mempool, warnings,
+                                     PeerManager::Options{
+                                         .reconcile_txs = true,
+                                         .deterministic_rng = true,
+                                     });
+
+    connman.SetMsgProc(peerman.get());
     LOCK(NetEventsInterface::g_msgproc_mutex);
 
     const std::string random_message_type{fuzzed_data_provider.ConsumeBytesAsString(CMessageHeader::MESSAGE_TYPE_SIZE).c_str()};
```

### src/test/fuzz/process_messages.cpp
```diff
@@ -5,6 +5,7 @@
 #include <consensus/consensus.h>
 #include <net.h>
 #include <net_processing.h>
+#include <node/warnings.h>
 #include <protocol.h>
 #include <script/script.h>
 #include <sync.h>
@@ -30,9 +31,11 @@ const TestingSetup* g_setup;
 
 void initialize_process_messages()
 {
-    static const auto testing_setup = MakeNoLogFileContext<const TestingSetup>(
+    static const auto testing_setup{
+        MakeNoLogFileContext<TestingSetup>(
             /*chain_type=*/ChainType::REGTEST,
-            {.extra_args = {"-txreconciliation"}});
+            {}),
+    };
     g_setup = testing_setup.get();
     SetMockTime(WITH_LOCK(g_setup->m_node.chainman->GetMutex(), return g_setup->m_node.chainman->ActiveTip()->Time()));
     for (int i = 0; i < 2 * COINBASE_MATURITY; i++) {
@@ -46,11 +49,23 @@ FUZZ_TARGET(process_messages, .init = initialize_process_messages)
     SeedRandomStateForTest(SeedRand::ZEROS);
     FuzzedDataProvider fuzzed_data_provider(buffer.data(), buffer.size());
 
-    ConnmanTestMsg& connman = *static_cast<ConnmanTestMsg*>(g_setup->m_node.connman.get());
+    auto& connman = static_cast<ConnmanTestMsg&>(*g_setup->m_node.connman);
     auto& chainman = static_cast<TestChainstateManager&>(*g_setup->m_node.chainman);
     SetMockTime(1610000000); // any time to successfully reset ibd
     chainman.ResetIbd();
 
+    node::Warnings warnings{};
+    NetGroupManager netgroupman{{}};
+    AddrMan addrman{netgroupman, /*deterministic=*/true, /*consistency_check_ratio=*/0};
+    auto peerman = PeerManager::make(connman, addrman,
+                                     /*banman=*/nullptr, chainman,
+                                     *g_setup->m_node.mempool, warnings,
+                                     PeerManager::Options{
+                                         .reconcile_txs = true,
+                                         .deterministic_rng = true,
+                                     });
+    connman.SetMsgProc(peerman.get());
+
     LOCK(NetEventsInterface::g_msgproc_mutex);
 
     std::vector<CNode*> peers;
```
