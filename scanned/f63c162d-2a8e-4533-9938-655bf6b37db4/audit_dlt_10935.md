# [?] Fix the deadlock

## Summary
Severity: Unknown
Chain: Zilliqa
Component: Zilliqa/zq1
Published: 2018-12-13
Source: https://github.com/Zilliqa/zq1/commit/97e6cce13badcbc91c8058669bda38fd45a28fab
Type: security-commit

## Details
Fix the deadlock

## Patch
### src/libLookup/Lookup.cpp
```diff
@@ -88,6 +88,10 @@ void Lookup::InitSync() {
     uint64_t dsBlockNum = 0;
     uint64_t txBlockNum = 0;
 
+    // Hack to allow seed server to be restarted so as to get my newlookup ip
+    // and register me with multiplier.
+    this_thread::sleep_for(chrono::seconds(NEW_LOOKUP_SYNC_DELAY));
+
     // Initialize all blockchains and blocklinkchain
     InitAsNewJoiner();
 
@@ -109,8 +113,6 @@ void Lookup::InitSync() {
 
       this_thread::sleep_for(chrono::seconds(NEW_NODE_SYNC_INTERVAL));
     }
-    // Register myself with multiplier.
-    // TBD
   };
   DetachedFunction(1, func);
 }
@@ -2694,21 +2696,27 @@ bool Lookup::GetMyLookupOnline() {
   }
 
   LOG_MARKER();
+  bool found = false;
+  {
+    std::lock_guard<std::mutex> lock(m_mutexLookupNodes);
+    auto selfPeer(m_mediator.m_selfPeer);
+    auto iter =
+        std::find_if(m_lookupNodesOffline.begin(), m_lookupNodesOffline.end(),
+                     [&selfPeer](const std::pair<PubKey, Peer>& node) {
+                       return node.second == selfPeer;
+                     });
+    if (iter != m_lookupNodesOffline.end()) {
+      found = true;
+      m_lookupNodes.emplace_back(*iter);
+      m_lookupNodesOffline.erase(iter);
+    } else {
+      LOG_GENERAL(WARNING, "My Peer Info is not in m_lookupNodesOffline");
+      return false;
+    }
+  }
 
-  std::lock_guard<std::mutex> lock(m_mutexLookupNodes);
-  auto selfPeer(m_mediator.m_selfPeer);
-  auto iter =
-      std::find_if(m_lookupNodesOffline.begin(), m_lookupNodesOffline.end(),
-                   [&selfPeer](const std::pair<PubKey, Peer>& node) {
-                     return node.second == selfPeer;
-                   });
-  if (iter != m_lookupNodesOffline.end()) {
+  if (found) {
     SendMessageToLookupNodesSerial(ComposeGetLookupOnlineMessage());
-    m_lookupNodes.emplace_back(*iter);
-    m_lookupNodesOffline.erase(iter);
-  } else {
-    LOG_GENERAL(WARNING, "My Peer Info is not in m_lookupNodesOffline");
-    return false;
   }
   return true;
 }
```
