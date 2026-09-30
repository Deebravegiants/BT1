# [?] fix(sync): stop scoring the serving peer for far-ahead blocks (GHSA-qhr3-cvch-5fh2)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-08-03
Source: https://github.com/ZcashFoundation/zebra/commit/324dea07dd48e278d32f06c8cb8f52dac43b6b38
Type: security-commit

## Details
fix(sync): stop scoring the serving peer for far-ahead blocks (GHSA-qhr3-cvch-5fh2)

During integration with GHSA-g95h-hw6g-pvgv, preserve the explicit
behind-tip scoring arm while leaving above-lookahead responses
deliberately unscored. Retain both security changelog entries.

Conflicts:
    CHANGELOG.md
    zebrad/src/components/sync.rs

## Patch
### CHANGELOG.md
```diff
@@ -63,6 +63,10 @@ and this project adheres to [Semantic Versioning](https://semver.org).
   peer's IPv4 address did not disconnect it while it stayed connected, and the same peer counted
   twice towards the per-IP inbound connection limit
   ([#10695](https://github.com/ZcashFoundation/zebra/issues/10695)).
+- Blocks above the sync lookahead height limit no longer score the peer that served them.
+  A `FindBlocks` response does not record who supplied its hashes, so the block request is
+  routed to an unrelated honest peer, and scoring it let a malicious peer get honest peers
+  banned throughout initial block download (GHSA-qhr3-cvch-5fh2)
 
 ## [Zebra 6.2.3](https://github.com/ZcashFoundation/zebra/releases/tag/v6.2.3) - 2026-07-27
 
```

### zebrad/src/components/sync.rs
```diff
@@ -1214,13 +1214,6 @@ where
                     .try_send((advertiser_addr, error.misbehavior_score()));
             }
 
-            Err(BlockDownloadVerifyError::AboveLookaheadHeightLimit {
-                advertiser_addr: Some(advertiser_addr),
-                ..
-            }) => {
-                let _ = self.misbehavior_sender.try_send((advertiser_addr, 100));
-            }
-
             Err(BlockDownloadVerifyError::InvalidHeight {
                 advertiser_addr: Some(advertiser_addr),
                 ..
@@ -1241,6 +1234,18 @@ where
                 let _ = self.misbehavior_sender.try_send((advertiser_addr, 100));
             }
 
+            // `AboveLookaheadHeightLimit` deliberately falls through unscored, and must stay
+            // that way (GHSA-qhr3-cvch-5fh2). GHSA-gvjc-3w7c-92jx originally scored
+            // `advertiser_addr` 100 here, but that names the peer that *served* the block,
+            // not the one that chose its height: `Response::BlockHashes` carries no address
+            // and multi-block `inv`s are never registered as inventory, so the follow-up
+            // getdata goes to an independently chosen, honest peer. Scoring it let a
+            // malicious `FindBlocks` responder evict honest peers throughout IBD.
+            //
+            // Unlike the behind-tip sibling advisory, the block here is genuine, so there is
+            // no local proof of forgery to re-attribute with. The block is still dropped in
+            // `downloads.rs` and the hash is re-requested once our tip advances. Do not
+            // restore symmetry with the arms above by adding scoring back.
             Err(_) => {}
         };
 
```
