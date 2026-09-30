# [?] fix(sync): stop scoring the serving peer for far-ahead blocks (GHSA-qhr3-cvch-5fh2)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-08-05
Source: https://github.com/ZcashFoundation/zebra/commit/80376c71c1307335f9c4941b374d18778b55ca21
Type: security-commit

## Details
fix(sync): stop scoring the serving peer for far-ahead blocks (GHSA-qhr3-cvch-5fh2)

## Patch
### CHANGELOG.md
```diff
@@ -63,6 +63,10 @@ and this project adheres to [Semantic Versioning](https://semver.org).
   peer's IPv4 address did not disconnect it while it stayed connected, and the same peer counted
   twice towards the per-IP inbound connection limit
   ([#10695](https://github.com/ZcashFoundation/zebra/issues/10695)).
+- Blocks above the sync lookahead height limit no longer score the peer that served
+  them, since that request is routed to an unrelated honest peer — scoring it let a
+  malicious `FindBlocks` responder get honest peers banned during initial block
+  download (GHSA-qhr3-cvch-5fh2)
 
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
@@ -1241,6 +1234,14 @@ where
                 let _ = self.misbehavior_sender.try_send((advertiser_addr, 100));
             }
 
+            // `AboveLookaheadHeightLimit` deliberately falls through unscored, and must
+            // stay that way (GHSA-qhr3-cvch-5fh2): `advertiser_addr` names the peer that
+            // *served* the block, not the one that chose its height — `FindBlocks`
+            // responses carry no address, so the follow-up request goes to an
+            // independently chosen, honest peer, and scoring it let a malicious
+            // `FindBlocks` responder evict honest peers throughout IBD. Unlike the
+            // behind-tip sibling advisory, the block here is genuine, so there is no
+            // local proof of forgery to re-attribute with. Do not add scoring back.
             Err(_) => {}
         };
 
```

### zebrad/src/components/sync/tests/vectors.rs
```diff
@@ -10,6 +10,7 @@ use futures::{Future, FutureExt};
 use zebra_chain::{
     block::{self, Block, Height},
     chain_tip::mock::{MockChainTip, MockChainTipSender},
+    parameters::subsidy::SubsidyError,
     serialization::ZcashDeserializeInto,
 };
 use zebra_consensus::{Config as ConsensusConfig, RouterError, VerifyBlockError};
@@ -1323,31 +1324,6 @@ async fn above_lookahead_does_not_restart_sync() {
     );
 }
 
-/// Verifies fix for GHSA-gvjc-3w7c-92jx: `AboveLookaheadHeightLimit` now
-/// carries `advertiser_addr` so the offending peer can be scored.
-#[tokio::test]
-async fn above_lookahead_has_peer_attribution() {
-    let addr: PeerSocketAddr = "127.0.0.1:8233".parse().unwrap();
-    let err = BlockDownloadVerifyError::AboveLookaheadHeightLimit {
-        height: block::Height(60_000),
-        hash: block::Hash::from([0xCC; 32]),
-        advertiser_addr: Some(addr),
-    };
-
-    let has_addr = match &err {
-        BlockDownloadVerifyError::AboveLookaheadHeightLimit {
-            advertiser_addr, ..
-        } => advertiser_addr.is_some(),
-        _ => false,
-    };
-
-    assert!(
-        has_addr,
-        "AboveLookaheadHeightLimit should carry advertiser_addr for peer scoring \
-         (GHSA-gvjc-3w7c-92jx fix)"
-    );
-}
-
 /// Verifies fix for GHSA-gvjc-3w7c-92jx: both height-limit errors now
 /// return `false` from `should_restart_sync` — symmetric handling.
 #[tokio::test]
@@ -1576,6 +1552,58 @@ async fn download_failed_is_only_requeued_for_not_found() {
     );
 }
 
+/// Verifies fix for GHSA-qhr3-cvch-5fh2: a block that lands above the lookahead
+/// height limit must NOT score the peer that served it, while consensus-invalid
+/// blocks still must.
+///
+/// Far-ahead hashes from a malicious `FindBlocks` response carry no peer attribution,
+/// so the follow-up `BlocksByHash` request is routed to an independently chosen,
+/// honest peer — `advertiser_addr` names the *serving* peer, not the peer that chose
+/// the height. Scoring this path bans honest peers at the attacker's direction.
+#[tokio::test]
+async fn far_ahead_block_does_not_score_serving_peer() {
+    let (mut chain_sync, mut misbehavior_rx) = new_chain_sync_with_misbehavior();
+
+    let peer: PeerSocketAddr = "127.0.0.1:8233".parse().unwrap();
+
+    // Positive control, and proof the channel plumbing works: a consensus-invalid
+    // block with a non-zero score must still be reported.
+    let router_error = RouterError::Block {
+        source: Box::new(VerifyBlockError::Subsidy(SubsidyError::NoCoinbase)),
+    };
+    let expected_score = router_error.misbehavior_score();
+    assert_ne!(
+        expected_score, 0,
+        "this control needs an error with a non-zero misbehavior score"
+    );
+
+    let _ = chain_sync.handle_block_response(Err(BlockDownloadVerifyError::Invalid {
+        error: router_error,
+        height: block::Height(60_000),
+        hash: block::Hash::from([0xAB; 32]),
+        advertiser_addr: Some(peer),
+    }));
+    assert_eq!(
+        misbehavior_rx.try_recv(),
+        Ok((peer, expected_score)),
+        "consensus-invalid blocks must still score the serving peer"
+    );
+
+    // The fix: an above-lookahead block must not produce any misbehavior score.
+    let _ = chain_sync.handle_block_response(Err(
+        BlockDownloadVerifyError::AboveLookaheadHeightLimit {
+            height: block::Height(60_000),
+            hash: block::Hash::from([0xBB; 32]),
+            advertiser_addr: Some(peer),
+        },
+    ));
+    assert_eq!(
+        misbehavior_rx.try_recv(),
+        Err(tokio::sync::mpsc::error::TryRecvError::Empty),
+        "GHSA-qhr3-cvch-5fh2: an above-lookahead block must not score the serving peer"
+    );
+}
+
 /// Build a [`ChainSync`] wired to mock services, returning the receiver end of the misbehavior
 /// channel so a test can assert whether a peer was scored.
 ///
```
