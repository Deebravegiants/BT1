# [?] Merge pull request #1046 from Zilliqa/fix/deadlock-mutexLookupNodes

## Summary
Severity: Unknown
Chain: Zilliqa
Component: Zilliqa/zq1
Published: 2018-12-14
Source: https://github.com/Zilliqa/zq1/commit/f15d3edee7cf3d90fd724b34b74dd09ad8331ce4
Type: security-commit

## Details
Merge pull request #1046 from Zilliqa/fix/deadlock-mutexLookupNodes

Fix the deadlock on mutex m_mutexLookupNodes + Delay starting new lookup syncup

## Patch
### constants.xml
```diff
@@ -43,6 +43,7 @@
         <POW_WINDOW_IN_SECONDS>150</POW_WINDOW_IN_SECONDS>
         <RECOVERY_SYNC_TIMEOUT>5</RECOVERY_SYNC_TIMEOUT>
         <TX_DISTRIBUTE_TIME_IN_MS>30000</TX_DISTRIBUTE_TIME_IN_MS>
+        <NEW_LOOKUP_SYNC_DELAY_IN_SECONDS>180</NEW_LOOKUP_SYNC_DELAY_IN_SECONDS>
     </epoch_timing>
     <fallback>
         <ENABLE_FALLBACK>false</ENABLE_FALLBACK>
```

### constants_local.xml
```diff
@@ -43,6 +43,7 @@
         <POW_WINDOW_IN_SECONDS>30</POW_WINDOW_IN_SECONDS>
         <RECOVERY_SYNC_TIMEOUT>5</RECOVERY_SYNC_TIMEOUT>
         <TX_DISTRIBUTE_TIME_IN_MS>10000</TX_DISTRIBUTE_TIME_IN_MS>
+        <NEW_LOOKUP_SYNC_DELAY_IN_SECONDS>60</NEW_LOOKUP_SYNC_DELAY_IN_SECONDS>
     </epoch_timing>
     <fallback>
         <ENABLE_FALLBACK>false</ENABLE_FALLBACK>
```

### src/common/Constants.cpp
```diff
@@ -130,6 +130,8 @@ const unsigned int RECOVERY_SYNC_TIMEOUT{
     ReadConstantNumeric("RECOVERY_SYNC_TIMEOUT", "node.epoch_timing.")};
 const unsigned int TX_DISTRIBUTE_TIME_IN_MS{
     ReadConstantNumeric("TX_DISTRIBUTE_TIME_IN_MS", "node.epoch_timing.")};
+const unsigned int NEW_LOOKUP_SYNC_DELAY_IN_SECONDS{ReadConstantNumeric(
+    "NEW_LOOKUP_SYNC_DELAY_IN_SECONDS", "node.epoch_timing.")};
 
 // Fallback constants
 const bool ENABLE_FALLBACK{
```

### src/common/Constants.h
```diff
@@ -147,6 +147,7 @@ extern const unsigned int POW_SUBMISSION_TIMEOUT;
 extern const unsigned int POW_WINDOW_IN_SECONDS;
 extern const unsigned int RECOVERY_SYNC_TIMEOUT;
 extern const unsigned int TX_DISTRIBUTE_TIME_IN_MS;
+extern const unsigned int NEW_LOOKUP_SYNC_DELAY_IN_SECONDS;
 
 // Fallback constants
 extern const bool ENABLE_FALLBACK;
```

### src/libLookup/Lookup.cpp
```diff
@@ -88,6 +88,10 @@ void Lookup::InitSync() {
     uint64_t dsBlockNum = 0;
     uint64_t txBlockNum = 0;
 
+    // Hack to allow seed server to be restarted so as to get my newlookup ip
+    // and register me with multiplier.
+    this_thread::sleep_for(chrono::seconds(NEW_LOOKUP_SYNC_DELAY_IN_SECONDS));
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
