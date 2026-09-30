# [?] test(sync): add failing regression test for GHSA-qhr3-cvch-5fh2 far-ahead block attribution

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-08-03
Source: https://github.com/ZcashFoundation/zebra/commit/f844bbecbe360d3a49316ec5b8cba18cce63aa8d
Type: security-commit

## Details
test(sync): add failing regression test for GHSA-qhr3-cvch-5fh2 far-ahead block attribution

During integration with GHSA-g95h-hw6g-pvgv, preserve both sets of
regression tests and reuse the newer shared ChainSync test helper,
including its separate read-state service.

Conflicts:
    zebrad/src/components/sync/tests/vectors.rs

## Patch
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
@@ -1576,6 +1577,81 @@ async fn download_failed_is_only_requeued_for_not_found() {
     );
 }
 
+/// Verifies fix for GHSA-qhr3-cvch-5fh2: a block that lands above the lookahead
+/// height limit must NOT score the peer that served it.
+///
+/// A malicious peer can answer `FindBlocks` with real but far-ahead block hashes.
+/// Those hashes carry no peer attribution, and `FindBlocks` suppliers are never
+/// registered in the inventory registry, so the follow-up `BlocksByHash` getdata is
+/// routed to an independently chosen, honest peer. That honest peer returns exactly
+/// the block we asked for, the download fails with `AboveLookaheadHeightLimit`, and
+/// `advertiser_addr` names the *serving* peer, not the peer that supplied the hash.
+/// Scoring on this path therefore bans an honest peer at the attacker's direction.
+///
+/// This drives the real [`ChainSync::handle_block_response`] method and asserts that
+/// nothing at all reaches the misbehavior channel.
+#[tokio::test]
+async fn far_ahead_block_does_not_score_serving_peer() {
+    let (mut chain_sync, mut misbehavior_rx) = new_chain_sync_with_misbehavior();
+
+    let serving_peer: PeerSocketAddr = "127.0.0.1:8233".parse().unwrap();
+
+    let _ = chain_sync.handle_block_response(Err(
+        BlockDownloadVerifyError::AboveLookaheadHeightLimit {
+            height: block::Height(60_000),
+            hash: block::Hash::from([0xBB; 32]),
+            advertiser_addr: Some(serving_peer),
+        },
+    ));
+
+    let received = misbehavior_rx.try_recv();
+
+    assert_eq!(
+        received,
+        Err(tokio::sync::mpsc::error::TryRecvError::Empty),
+        "GHSA-qhr3-cvch-5fh2: an above-lookahead block must not produce any misbehavior \
+         score. `advertiser_addr` here is the peer that *served* the block we explicitly \
+         requested, not the peer that supplied the far-ahead hash, so scoring it lets a \
+         malicious peer get arbitrary honest peers banned. Got: {received:?}"
+    );
+}
+
+/// Positive control for the GHSA-qhr3-cvch-5fh2 fix: removing the above-lookahead
+/// scoring must not disable misbehavior scoring in general.
+///
+/// A `BlockDownloadVerifyError::Invalid` with a non-zero `misbehavior_score()` and a
+/// known advertiser still has to reach the misbehavior channel. This test passes both
+/// before and after the fix.
+#[tokio::test]
+async fn invalid_block_still_scores_advertising_peer() {
+    let (mut chain_sync, mut misbehavior_rx) = new_chain_sync_with_misbehavior();
+
+    let advertiser: PeerSocketAddr = "127.0.0.1:8233".parse().unwrap();
+
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
+        advertiser_addr: Some(advertiser),
+    }));
+
+    assert_eq!(
+        misbehavior_rx.try_recv(),
+        Ok((advertiser, expected_score)),
+        "consensus-invalid blocks must still score the advertising peer — the \
+         GHSA-qhr3-cvch-5fh2 fix only removes the above-lookahead attribution"
+    );
+}
+
 /// Build a [`ChainSync`] wired to mock services, returning the receiver end of the misbehavior
 /// channel so a test can assert whether a peer was scored.
 ///
```
