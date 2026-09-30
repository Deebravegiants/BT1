# [?] rpc: fix crash in getcompactsketch

## Summary
Severity: Unknown
Chain: Liquid
Component: ElementsProject/elements
Published: 2025-02-11
Source: https://github.com/ElementsProject/elements/commit/bd4ae1bcc405c3496c85c3af16c81a0768f82392
Type: security-commit

## Details
rpc: fix crash in getcompactsketch

This originates in 8723debb3d1f281f26bdc456868f3daaf7c6aa5a which has no
PR associated with it. We've really gotta stop putting thousands of
unreviewed commits into this project and rebasing the history away..

## Patch
### src/rpc/mining.cpp
```diff
@@ -1527,6 +1527,10 @@ static RPCHelpMan getcompactsketch()
     CDataStream ssBlock(block_bytes, SER_NETWORK, PROTOCOL_VERSION);
     ssBlock >> block;
 
+    if (block.vtx.empty()) {
+        throw JSONRPCError(RPC_DESERIALIZATION_ERROR, "Cannot obtain sketch of empty block.");
+    }
+
     CBlockHeaderAndShortTxIDs cmpctblock(block, true);
 
     CDataStream ssCompactBlock(SER_NETWORK, PROTOCOL_VERSION);
```
