# [?] net: cast vector size to avoid overflow, truncation, sign change

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoin/bitcoin
Published: 2026-09-24
Source: https://github.com/bitcoin/bitcoin/commit/308cd670195d908fbd50caf76a8a215386121bd0
Type: security-commit

## Details
net: cast vector size to avoid overflow, truncation, sign change

## Patch
### src/net_processing.cpp
```diff
@@ -3659,7 +3659,7 @@ void PeerManagerImpl::ProcessGetCFCheckPt(CNode& node, Peer& peer, DataStream& v
 
     // Populate headers.
     const CBlockIndex* block_index = stop_index;
-    for (int i = headers.size() - 1; i >= 0; i--) {
+    for (int i = int(headers.size()) - 1; i >= 0; i--) {
         int height = (i + 1) * CFCHECKPT_INTERVAL;
         block_index = block_index->GetAncestor(height);
 
```
