# [?] Fix crash

## Summary
Severity: Unknown
Chain: Zilliqa
Component: Zilliqa/zq1
Published: 2018-12-10
Source: https://github.com/Zilliqa/zq1/commit/422d060354ffdd0f935fbce88414484614d015b5
Type: security-commit

## Details
Fix crash

## Patch
### src/libServer/Server.cpp
```diff
@@ -76,18 +76,16 @@ Server::~Server() {
 string Server::GetNetworkId() { return "TestNet"; }
 
 bool Server::StartCollectorThread() {
-  vector<Transaction> txns;
-
   if (!LOOKUP_NODE_MODE || !ARCHIVAL_LOOKUP) {
     LOG_GENERAL(
         WARNING,
         "Not expected to be called from node other than LOOKUP ARCHIVAL ");
     return false;
   }
-  auto collectorThread = [this, &txns]() mutable -> void {
+  auto collectorThread = [this]() mutable -> void {
     this_thread::sleep_for(chrono::seconds(120));  //[Remove this]
                                                    // Change Back
-
+    vector<Transaction> txns;
     // Change Back
     LOG_GENERAL(INFO, "[ARCHLOOK]"
                           << "Start thread");
```
