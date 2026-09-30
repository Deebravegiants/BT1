# [?] Fix recover community testnet lookup and it crash

## Summary
Severity: Unknown
Chain: Zilliqa
Component: Zilliqa/zq1
Published: 2019-09-09
Source: https://github.com/Zilliqa/zq1/commit/310928490855ec8a5cb4f99ec5f8bcad08b24d7e
Type: security-commit

## Details
Fix recover community testnet lookup and it crash

## Patch
### src/libLookup/Lookup.cpp
```diff
@@ -3348,8 +3348,10 @@ void Lookup::RejoinAsLookup() {
   LOG_MARKER();
 
   if (m_mediator.m_lookup->GetSyncType() == SyncType::NO_SYNC) {
-    m_lookupServer->StopListening();
-    LOG_GENERAL(INFO, "API Server stopped listen for syncing");
+    if (m_lookupServer) {
+      m_lookupServer->StopListening();
+      LOG_GENERAL(INFO, "API Server stopped listen for syncing");
+    }
 
     auto func = [this]() mutable -> void {
       m_mediator.m_lookup->SetSyncType(SyncType::LOOKUP_SYNC);
```
