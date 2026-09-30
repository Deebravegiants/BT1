# [?] cherrypick: fix crash when block without blobs is unqueued from quarantine #7543

## Summary
Severity: Unknown
Chain: Ethereum
Component: status-im/nimbus-eth2
Published: 2025-09-26
Source: https://github.com/status-im/nimbus-eth2/commit/2b8fb6f669ad16b7fec0e52feeea6b678b2388ce
Type: security-commit

## Details
cherrypick: fix crash when block without blobs is unqueued from quarantine #7543

## Patch
### beacon_chain/gossip_processing/block_processor.nim
```diff
@@ -426,7 +426,7 @@ proc enqueueQuarantine(self: var BlockProcessor, root: Eth2Digest) =
           self.enqueueBlock(
             MsgSource.gossip,
             quarantined,
-            Opt.some(BlobSidecars @[]),
+            Opt.none(BlobSidecars),
             Opt.some(DataColumnSidecars @[]),
           )
         else:
@@ -449,7 +449,7 @@ proc enqueueQuarantine(self: var BlockProcessor, root: Eth2Digest) =
             MsgSource.gossip,
             quarantined,
             Opt.some(BlobSidecars @[]),
-            Opt.some(DataColumnSidecars @[]),
+            Opt.none(DataColumnSidecars),
           )
         else:
           if (let res = checkBlobOrColumnlessSignature(self, forkyBlck); res.isErr):
```
