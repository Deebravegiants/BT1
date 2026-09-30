# [?] merge: GHSA-4f6v-mj46-gxg3 into combined-security-fixes-ci

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-09-17
Source: https://github.com/ZcashFoundation/zebra/commit/6dbee3a62eb9f246694d2d3732597a6ffbfe7bf9
Type: security-commit

## Details
merge: GHSA-4f6v-mj46-gxg3 into combined-security-fixes-ci

## Patch
### .changes/unreleased/zebrad-Security-20260821-165239.yaml
```diff
@@ -0,0 +1,7 @@
+project: zebrad
+kind: Security
+body: >
+  Penalize coinbase scriptSig rewrite in inbound path
+  ([GHSA-4f6v-mj46-gxg3](https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-4f6v-mj46-gxg3)).
+  Thanks to @craftsoldier for reporting the issue.
+time: 2026-08-21T16:52:39.000000000Z
```

### zebrad/src/components/inbound.rs
```diff
@@ -48,7 +48,7 @@ use cached_peer_addr_response::CachedPeerAddrResponse;
 #[cfg(test)]
 mod tests;
 
-use downloads::Downloads as BlockDownloads;
+use downloads::{Downloads as BlockDownloads, HeightLimitError};
 
 /// The maximum amount of time an inbound service response can take.
 ///
@@ -83,8 +83,12 @@ type SemanticBlockVerifier = Buffer<
     BoxService<zebra_consensus::Request, block::Hash, RouterError>,
     zebra_consensus::Request,
 >;
-type GossipedBlockDownloads =
-    BlockDownloads<Timeout<BlockDownloadPeerSet>, Timeout<SemanticBlockVerifier>, State>;
+type GossipedBlockDownloads = BlockDownloads<
+    Timeout<BlockDownloadPeerSet>,
+    Timeout<SemanticBlockVerifier>,
+    State,
+    zs::LatestChainTip,
+>;
 
 /// The services used by the [`Inbound`] service.
 pub struct InboundSetupData {
@@ -352,6 +356,14 @@ impl Service<zn::Request> for Inbound {
                         err.misbehavior_score()
                     } else if let Some(err) = err.downcast_ref::<VerifyBlockError>() {
                         err.misbehavior_score()
+                    } else if let Some(err) = err.downcast_ref::<HeightLimitError>() {
+                        // A gossiped block dropped before the verifier because its coinbase height
+                        // was outside the accepted range around the tip. The downloader only
+                        // attaches an advertiser address to these drops when the parent header
+                        // Zebra holds contradicts the claimed height, which proves the height was
+                        // rewritten (GHSA-4f6v-mj46-gxg3), so honest peers serving genuinely old or
+                        // far-ahead blocks are never scored.
+                        err.misbehavior_score()
                     } else {
                         continue;
                     };
```

### zebrad/src/components/inbound/downloads.rs
```diff
@@ -1,10 +1,14 @@
 //! A download stream that handles gossiped blocks from peers.
 
+#[cfg(test)]
+mod tests;
+
 use std::{
     collections::{HashMap, HashSet},
     net::IpAddr,
     pin::Pin,
     task::{Context, Poll},
+    time::Duration,
 };
 
 use futures::{
@@ -13,7 +17,8 @@ use futures::{
     stream::{FuturesUnordered, Stream},
 };
 use pin_project::pin_project;
-use tokio::{sync::oneshot, task::JoinHandle};
+use thiserror::Error;
+use tokio::{sync::oneshot, task::JoinHandle, time::timeout};
 use tower::{Service, ServiceExt};
 use tracing_futures::Instrument;
 
@@ -28,6 +33,102 @@ use crate::components::sync::MIN_CONCURRENCY_LIMIT;
 
 type BoxError = Box<dyn std::error::Error + Send + Sync + 'static>;
 
+/// How long to wait for the parent-height lookup that decides whether a behind-tip gossiped block
+/// was forged.
+///
+/// Bounds a drop path that also fires for honest old blocks. Timing out is treated as "no proof",
+/// so a slow state read costs the supplying peer nothing.
+const PARENT_LOOKUP_TIMEOUT: Duration = Duration::from_secs(5);
+
+/// A gossiped block was dropped before verification because its coinbase height was outside the
+/// accepted range around the chain tip.
+///
+/// Peers legitimately serve blocks that are genuinely far ahead of the tip while Zebra is catching
+/// up, and blocks that are genuinely older than the finalized tip, so this error is returned for
+/// every such drop. But a peer can also answer a [`BlocksByHash`](zn::Request::BlocksByHash) request
+/// with a canonical header and a rewritten coinbase height, because the coinbase scriptSig is
+/// excluded from the V5 transaction ID and therefore from the block hash (ZIP-244). The initial hash
+/// check still passes, so the forged height reaches these drops before consensus validation, and the
+/// verifier never scores the peer (GHSA-4f6v-mj46-gxg3).
+///
+/// The downloader attaches the supplying peer's address to the drop only when the parent header
+/// Zebra already holds proves the claimed height wrong (see [`advertiser_if_parent_contradicts`]),
+/// so the inbound handler scores a proven rewrite, and never an authentic block.
+///
+/// This is the inbound-gossip sibling of the sync path's height limit errors (GHSA-g95h-hw6g-pvgv).
+#[derive(Copy, Clone, Debug, Error)]
+pub enum HeightLimitError {
+    /// The block's coinbase height is above the lookahead limit.
+    #[error("gossiped block height {height:?} too far ahead of the tip: {hash:?}")]
+    AboveLookahead {
+        height: block::Height,
+        hash: block::Hash,
+    },
+
+    /// The block's coinbase height is behind the finalized tip.
+    #[error("gossiped block height {height:?} behind the finalized tip: {hash:?}")]
+    BehindTip {
+        height: block::Height,
+        hash: block::Hash,
+    },
+}
+
+impl HeightLimitError {
+    /// The misbehavior score for a gossiped block whose parent proves its height was rewritten.
+    ///
+    /// A rewritten coinbase height is unambiguous misbehavior whichever limit it crossed, so score it
+    /// at the ban threshold, matching the sync path (GHSA-g95h-hw6g-pvgv).
+    pub fn misbehavior_score(&self) -> u32 {
+        zn::constants::MAX_PEER_MISBEHAVIOR_SCORE
+    }
+}
+
+/// Returns `advertiser_addr` if the parent header Zebra already holds proves that a gossiped block's
+/// claimed `block_height` was rewritten, and `None` if there is no such proof.
+///
+/// # Security
+///
+/// A peer can answer a `BlocksByHash` request with a canonical header and a rewritten coinbase
+/// height, because the coinbase scriptSig is excluded from the V5 transaction ID and therefore from
+/// the block hash (ZIP-244). The hash check passes, so the forged height reaches the height limit
+/// drops before consensus validation. Peers also legitimately serve blocks that are genuinely far
+/// ahead of the tip or genuinely older than the finalized tip, so the drop is only attributed to the
+/// supplying peer when the parent header Zebra holds contradicts the claimed height: a block's height
+/// is one more than its parent's, so a held parent whose height disagrees proves the body was
+/// rewritten, whichever limit the claimed height crossed.
+///
+/// A parent Zebra does not hold, a height consistent with the parent, and a failed or timed-out
+/// lookup are all treated as no proof, so honest peers are never scored and a slow state read costs
+/// the peer nothing. (GHSA-4f6v-mj46-gxg3, the inbound-gossip sibling of GHSA-g95h-hw6g-pvgv.)
+async fn advertiser_if_parent_contradicts<ZS>(
+    state: ZS,
+    parent_hash: block::Hash,
+    block_height: block::Height,
+    advertiser_addr: Option<PeerSocketAddr>,
+) -> Option<PeerSocketAddr>
+where
+    ZS: Service<zs::Request, Response = zs::Response, Error = BoxError> + Send + Clone + 'static,
+    ZS::Future: Send,
+{
+    // There is no peer to score, so skip the state lookup.
+    let advertiser_addr = advertiser_addr?;
+
+    match timeout(
+        PARENT_LOOKUP_TIMEOUT,
+        state.oneshot(zs::Request::BlockHeader(parent_hash.into())),
+    )
+    .await
+    {
+        Ok(Ok(zs::Response::BlockHeader {
+            height: parent_height,
+            ..
+        })) if (parent_height + 1) != Some(block_height) => Some(advertiser_addr),
+        // Parent unknown, height consistent with it, or the lookup failed or timed out: there is no
+        // proof of misbehavior, so the peer is not scored.
+        _ => None,
+    }
+}
+
 /// The maximum number of concurrent inbound download and verify tasks.
 /// Also used as the maximum lookahead limit, before block verification.
 ///
@@ -75,7 +176,7 @@ pub enum DownloadAction {
 /// Manages download and verification of blocks gossiped to this peer.
 #[pin_project]
 #[derive(Debug)]
-pub struct Downloads<ZN, ZV, ZS>
+pub struct Downloads<ZN, ZV, ZS, ZSTip>
 where
     ZN: Service<zn::Request, Response = zn::Response, Error = BoxError> + Send + Clone + 'static,
     ZN::Future: Send,
@@ -86,6 +187,7 @@ where
     ZV::Future: Send,
     ZS: Service<zs::Request, Response = zs::Response, Error = BoxError> + Send + Clone + 'static,
     ZS::Future: Send,
+    ZSTip: ChainTip + Clone + Send + 'static,
 {
     // Configuration
     //
@@ -105,7 +207,7 @@ where
     state: ZS,
 
     /// Allows efficient access to the best tip of the blockchain.
-    latest_chain_tip: zs::LatestChainTip,
+    latest_chain_tip: ZSTip,
 
     // Internal downloads state
     //
@@ -131,7 +233,7 @@ where
     in_flight_ips: HashSet<IpAddr>,
 }
 
-impl<ZN, ZV, ZS> Stream for Downloads<ZN, ZV, ZS>
+impl<ZN, ZV, ZS, ZSTip> Stream for Downloads<ZN, ZV, ZS, ZSTip>
 where
     ZN: Service<zn::Request, Response = zn::Response, Error = BoxError> + Send + Clone + 'static,
     ZN::Future: Send,
@@ -142,6 +244,7 @@ where
     ZV::Future: Send,
     ZS: Service<zs::Request, Response = zs::Response, Error = BoxError> + Send + Clone + 'static,
     ZS::Future: Send,
+    ZSTip: ChainTip + Clone + Send + 'static,
 {
     type Item = Result<block::Hash, (BoxError, Option<PeerSocketAddr>)>;
 
@@ -179,7 +282,7 @@ where
     }
 }
 
-impl<ZN, ZV, ZS> Downloads<ZN, ZV, ZS>
+impl<ZN, ZV, ZS, ZSTip> Downloads<ZN, ZV, ZS, ZSTip>
 where
     ZN: Service<zn::Request, Response = zn::Response, Error = BoxError> + Send + Clone + 'static,
     ZN::Future: Send,
@@ -190,6 +293,7 @@ where
     ZV::Future: Send,
     ZS: Service<zs::Request, Response = zs::Response, Error = BoxError> + Send + Clone + 'static,
     ZS::Future: Send,
+    ZSTip: ChainTip + Clone + Send + 'static,
 {
     /// Initialize a new download stream with the provided `network`, `verifier`, and `state` services.
     /// The `latest_chain_tip` must be linked to the provided `state` service.
@@ -202,7 +306,7 @@ where
         network: ZN,
         verifier: ZV,
         state: ZS,
-        latest_chain_tip: zs::LatestChainTip,
+        latest_chain_tip: ZSTip,
     ) -> Self {
         // The syncer already warns about the minimum.
         let full_verify_concurrency_limit =
@@ -286,7 +390,7 @@ where
 
         let fut = async move {
             // Check if the block is already in the state.
-            match state.oneshot(zs::Request::KnownBlock(hash)).await {
+            match state.clone().oneshot(zs::Request::KnownBlock(hash)).await {
                 Ok(zs::Response::KnownBlock(None)) => Ok(()),
                 Ok(zs::Response::KnownBlock(Some(_))) => Err("already present".into()),
                 Ok(_) => unreachable!("wrong response"),
@@ -375,7 +479,26 @@ where
                 );
                 metrics::counter!("gossip.max.height.limit.dropped.block.count").increment(1);
 
-                Err("gossiped block height too far ahead").map_err(|e| (e.into(), None))?;
+                // # Security
+                //
+                // Attribute the drop to the supplying peer only if the parent Zebra holds proves the
+                // claimed height was rewritten (GHSA-4f6v-mj46-gxg3). A genuinely far-ahead block
+                // has a parent Zebra does not hold yet, so it is dropped anonymously.
+                let advertiser_addr = advertiser_if_parent_contradicts(
+                    state,
+                    block.header.previous_block_hash,
+                    block_height,
+                    advertiser_addr,
+                )
+                .await;
+
+                return Err((
+                    BoxError::from(HeightLimitError::AboveLookahead {
+                        height: block_height,
+                        hash,
+                    }),
+                    advertiser_addr,
+                ));
             } else if block_height < min_accepted_height {
                 debug!(
                     ?hash,
@@ -387,8 +510,27 @@ where
                 );
                 metrics::counter!("gossip.min.height.limit.dropped.block.count").increment(1);
 
-                Err("gossiped block height behind the finalized tip")
-                    .map_err(|e| (e.into(), None))?;
+                // # Security
+                //
+                // Attribute the drop to the supplying peer only if the parent Zebra holds proves the
+                // claimed height was rewritten (GHSA-4f6v-mj46-gxg3). A genuinely old block is
+                // consistent with its parent, or has a parent Zebra does not hold, so it is dropped
+                // anonymously.
+                let advertiser_addr = advertiser_if_parent_contradicts(
+                    state,
+                    block.header.previous_block_hash,
+                    block_height,
+                    advertiser_addr,
+                )
+                .await;
+
+                return Err((
+                    BoxError::from(HeightLimitError::BehindTip {
+                        height: block_height,
+                        hash,
+                    }),
+                    advertiser_addr,
+                ));
             }
 
             verifier
```

### zebrad/src/components/inbound/downloads/tests.rs
```diff
@@ -0,0 +1,684 @@
+//! Fixed test vectors for the inbound gossip block download stream.
+//!
+//! These are the inbound-gossip siblings of the sync-path tests in
+//! `crate::components::sync::downloads::tests`: they cover GHSA-4f6v-mj46-gxg3, where a peer
+//! answers a `BlocksByHash` request with a canonical header and a rewritten coinbase height. The
+//! coinbase scriptSig is excluded from the V5 transaction ID (ZIP-244), so the block hash is
+//! unchanged and the response passes the hash check, but the forged height is dropped as too far
+//! ahead of the tip, or behind the finalized tip, before consensus validation. The supplying peer
+//! must be scored only when the parent header Zebra holds proves the height was rewritten.
+
+use std::{iter, sync::Arc, time::Duration};
+
+use futures::stream::StreamExt;
+
+use zebra_chain::{
+    block::{Block, Height},
+    chain_tip::mock::MockChainTip,
+    serialization::ZcashDeserializeInto,
+};
+use zebra_network::{InventoryResponse, PeerSocketAddr};
+use zebra_state::MAX_BLOCK_REORG_HEIGHT;
+use zebra_test::mock_service::{MockService, PanicAssertion};
+
+use zebra_network as zn;
+use zebra_state as zs;
+
+use super::{DownloadAction, Downloads, HeightLimitError, MIN_CONCURRENCY_LIMIT};
+
+use InventoryResponse::*;
+
+/// Maximum time to wait for a request to any test service.
+///
+/// These tests run the download task in parallel with the test, so machines under heavy load need a
+/// longer delay.
+const MAX_SERVICE_REQUEST_DELAY: Duration = Duration::from_millis(1000);
+
+/// A peer address used to check whether the supplying peer can be scored.
+const ADVERTISER: &str = "127.0.0.1:8233";
+
+type MockNetwork = MockService<zn::Request, zn::Response, PanicAssertion>;
+type MockVerifier = MockService<zebra_consensus::Request, zebra_chain::block::Hash, PanicAssertion>;
+type MockState = MockService<zs::Request, zs::Response, PanicAssertion>;
+
+/// Build an inbound gossip downloader whose state tip is at `tip_height`, returning the mock
+/// network, verifier, and state services so a test can drive and assert on them.
+#[allow(clippy::type_complexity)]
+fn mock_downloads(
+    tip_height: Height,
+) -> (
+    Downloads<MockNetwork, MockVerifier, MockState, MockChainTip>,
+    MockNetwork,
+    MockVerifier,
+    MockState,
+) {
+    let network: MockNetwork = MockService::build()
+        .with_max_request_delay(MAX_SERVICE_REQUEST_DELAY)
+        .for_unit_tests();
+
+    let verifier: MockVerifier = MockService::build()
+        .with_max_request_delay(MAX_SERVICE_REQUEST_DELAY)
+        .for_unit_tests();
+
+    let state: MockState = MockService::build()
+        .with_max_request_delay(MAX_SERVICE_REQUEST_DELAY)
+        .for_unit_tests();
+
+    let (latest_chain_tip, chain_tip_sender) = MockChainTip::new();
+    chain_tip_sender.send_best_tip_height(tip_height);
+    // Dropping the sender is fine: `watch::Receiver::borrow` keeps returning the height we just
+    // sent, and no test changes the tip mid-run.
+
+    let downloads = Downloads::new(
+        MIN_CONCURRENCY_LIMIT,
+        network.clone(),
+        verifier.clone(),
+        state.clone(),
+        latest_chain_tip,
+    );
+
+    (downloads, network, verifier, state)
+}
+
+/// Load the mainnet block 1 vector, which these tests use as a low-height block body.
+fn block_1() -> Arc<Block> {
+    zebra_test::vectors::BLOCK_MAINNET_1_BYTES
+        .zcash_deserialize_into()
+        .expect("hard-coded block vector deserializes")
+}
+
+/// Load the mainnet block 2 vector.
+fn block_2() -> Arc<Block> {
+    zebra_test::vectors::BLOCK_MAINNET_2_BYTES
+        .zcash_deserialize_into()
+        .expect("hard-coded block vector deserializes")
+}
+
+/// Load the mainnet genesis block vector.
+fn genesis() -> Arc<Block> {
+    zebra_test::vectors::BLOCK_MAINNET_GENESIS_BYTES
+        .zcash_deserialize_into()
+        .expect("hard-coded block vector deserializes")
+}
+
+/// Load the mainnet block 10 vector, which the far-ahead tests use as a high-height block body.
+fn block_10() -> Arc<Block> {
+    zebra_test::vectors::BLOCK_MAINNET_10_BYTES
+        .zcash_deserialize_into()
+        .expect("hard-coded block vector deserializes")
+}
+
+/// The tip height that puts block 2 exactly on the lookahead limit.
+///
+/// The downloader accepts blocks up to `MIN_CONCURRENCY_LIMIT` above the tip, so block 10 is far
+/// ahead of this tip, and block 2 is the highest block it still verifies.
+fn lookahead_boundary_tip() -> Height {
+    Height(2 - u32::try_from(MIN_CONCURRENCY_LIMIT).expect("small constant fits in u32"))
+}
+
+/// Regression test for GHSA-4f6v-mj46-gxg3: a gossiped body whose claimed height contradicts the
+/// parent we already hold is attributed to the peer that supplied it, and never reaches consensus.
+///
+/// A peer can answer with a canonical header and rewritten coinbase height because the initial hash
+/// check does not recompute the header's commitment to the body's authorizing data. The parent is
+/// the proof: a block's height is one more than its parent's.
+#[tokio::test]
+async fn contradicted_behind_tip_height_is_attributed_and_never_verified() {
+    let _init_guard = zebra_test::init();
+
+    // The tip is far enough ahead that a claimed height of 1 is behind the reorg limit.
+    let (mut downloads, mut network, mut verifier, mut state) =
+        mock_downloads(Height(2 * MAX_BLOCK_REORG_HEIGHT));
+
+    // Block 2's header with block 1's body: the hash and parent are block 2's, because the hash
+    // covers only the header, but the coinbase now claims height 1 instead of 2. This is the shape
+    // of the reported attack, without reproducing the hash-preserving rewrite itself.
+    let block_1 = block_1();
+    let block_2 = block_2();
+    let block = Arc::new(Block {
+        header: block_2.header.clone(),
+        transactions: block_1.transactions.clone(),
+    });
+    let hash = block.hash();
+    assert_eq!(
+        hash,
+        block_2.hash(),
+        "the block hash covers only the header"
+    );
+    assert_eq!(
+        block.coinbase_height(),
+        Some(Height(1)),
+        "the body must claim the height the downloader reads"
+    );
+
+    let advertiser: PeerSocketAddr = ADVERTISER.parse().expect("hard-coded address is valid");
+
+    assert!(
+        matches!(
+            downloads.download_and_verify(hash, Some(advertiser)),
+            DownloadAction::AddedToQueue
+        ),
+        "download is queued"
+    );
+
+    // The block is not already in the state.
+    state
+        .expect_request(zs::Request::KnownBlock(hash))
+        .await
+        .respond(zs::Response::KnownBlock(None));
+
+    network
+        .expect_request(zn::Request::BlocksByHash(iter::once(hash).collect()))
+        .await
+        .respond(zn::Response::Blocks(vec![Available((
+            block.clone(),
+            Some(advertiser),
+        ))]));
+
+    // We hold the real parent, block 1, so the body's real height is 2, not the 1 it claims.
+    state
+        .expect_request(zs::Request::BlockHeader(
+            block.header.previous_block_hash.into(),
+        ))
+        .await
+        .respond(zs::Response::BlockHeader {
+            header: block_1.header.clone(),
+            hash: block_1.hash(),
+            height: Height(1),
+            next_block_hash: Some(hash),
+        });
+
+    let (error, advertiser_addr) = downloads
+        .next()
+        .await
+        .expect("downloads is non-empty")
+        .expect_err("block behind the reorg limit is dropped");
+
+    assert!(
+        matches!(
+            error.downcast_ref::<HeightLimitError>(),
+            Some(HeightLimitError::BehindTip { .. })
+        ),
+        "a contradicted behind-tip height must be a scoreable typed error, but was: {error:?}"
+    );
+    assert_eq!(
+        advertiser_addr,
+        Some(advertiser),
+        "a contradicted behind-tip height must attribute the drop to the supplying peer"
+    );
+
+    // The rewritten body is dropped before consensus validation, which is why the peer must be
+    // scored on this path instead.
+    verifier.expect_no_requests().await;
+}
+
+/// A peer that serves a genuinely old block is not attributed, so it cannot be scored.
+///
+/// Its height agrees with its parent's, so there is no proof of misbehaviour and the drop must stay
+/// anonymous.
+#[tokio::test]
+async fn genuinely_old_block_is_dropped_without_attribution() {
+    let _init_guard = zebra_test::init();
+
+    let (mut downloads, mut network, mut verifier, mut state) =
+        mock_downloads(Height(2 * MAX_BLOCK_REORG_HEIGHT));
+
+    let block = block_1();
+    let hash = block.hash();
+    let advertiser: PeerSocketAddr = ADVERTISER.parse().expect("hard-coded address is valid");
+
+    assert!(
+        matches!(
+            downloads.download_and_verify(hash, Some(advertiser)),
+            DownloadAction::AddedToQueue
+        ),
+        "download is queued"
+    );
+
+    state
+        .expect_request(zs::Request::KnownBlock(hash))
+        .await
+        .respond(zs::Response::KnownBlock(None));
+
+    network
+        .expect_request(zn::Request::BlocksByHash(iter::once(hash).collect()))
+        .await
+        .respond(zn::Response::Blocks(vec![Available((
+            block.clone(),
+            Some(advertiser),
+        ))]));
+
+    // The parent is genesis, one below the height the body claims: the body is authentic.
+    let genesis = genesis();
+    assert_eq!(
+        block.header.previous_block_hash,
+        genesis.hash(),
+        "block 1's parent is genesis"
+    );
+    state
+        .expect_request(zs::Request::BlockHeader(
+            block.header.previous_block_hash.into(),
+        ))
+        .await
+        .respond(zs::Response::BlockHeader {
+            header: genesis.header.clone(),
+            hash: genesis.hash(),
+            height: Height(0),
+            next_block_hash: Some(hash),
+        });
+
+    let (error, advertiser_addr) = downloads
+        .next()
+        .await
+        .expect("downloads is non-empty")
+        .expect_err("block behind the reorg limit is dropped");
+
+    assert!(
+        matches!(
+            error.downcast_ref::<HeightLimitError>(),
+            Some(HeightLimitError::BehindTip { .. })
+        ),
+        "an old block must still be a typed behind-tip error, but was: {error:?}"
+    );
+    assert_eq!(
+        advertiser_addr, None,
+        "an authentic old block must not be attributed to its peer"
+    );
+
+    verifier.expect_no_requests().await;
+}
+
+/// A peer whose old block has a parent we do not hold is not attributed either: without the parent
+/// there is no proof the height was rewritten.
+#[tokio::test]
+async fn behind_tip_block_with_unknown_parent_is_not_attributed() {
+    let _init_guard = zebra_test::init();
+
+    let (mut downloads, mut network, mut verifier, mut state) =
+        mock_downloads(Height(2 * MAX_BLOCK_REORG_HEIGHT));
+
+    let block = block_1();
+    let hash = block.hash();
+    let advertiser: PeerSocketAddr = ADVERTISER.parse().expect("hard-coded address is valid");
+
+    assert!(
+        matches!(
+            downloads.download_and_verify(hash, Some(advertiser)),
+            DownloadAction::AddedToQueue
+        ),
+        "download is queued"
+    );
+
+    state
+        .expect_request(zs::Request::KnownBlock(hash))
+        .await
+        .respond(zs::Response::KnownBlock(None));
+
+    network
+        .expect_request(zn::Request::BlocksByHash(iter::once(hash).collect()))
+        .await
+        .respond(zn::Response::Blocks(vec![Available((
+            block.clone(),
+            Some(advertiser),
+        ))]));
+
+    state
+        .expect_request(zs::Request::BlockHeader(
+            block.header.previous_block_hash.into(),
+        ))
+        .await
+        .respond(Err(zn::BoxError::from("block not found in any chain")));
+
+    let (error, advertiser_addr) = downloads
+        .next()
+        .await
+        .expect("downloads is non-empty")
+        .expect_err("block behind the reorg limit is dropped");
+
+    assert!(
+        matches!(
+            error.downcast_ref::<HeightLimitError>(),
+            Some(HeightLimitError::BehindTip { .. })
+        ),
+        "a behind-tip drop must be a typed error, but was: {error:?}"
+    );
+    assert_eq!(
+        advertiser_addr, None,
+        "a block whose parent we do not hold must not be attributed"
+    );
+
+    verifier.expect_no_requests().await;
+}
+
+/// The parent lookup is bounded: when the state does not answer, the block is still dropped and the
+/// peer is still not attributed.
+///
+/// Paused time lets the runtime advance past `PARENT_LOOKUP_TIMEOUT` as soon as the download task is
+/// the only thing waiting, so the test does not sleep for real.
+#[tokio::test(start_paused = true)]
+async fn behind_tip_parent_lookup_timeout_is_not_attributed() {
+    let _init_guard = zebra_test::init();
+
+    let (mut downloads, mut network, mut verifier, mut state) =
+        mock_downloads(Height(2 * MAX_BLOCK_REORG_HEIGHT));
+
+    let block = block_1();
+    let hash = block.hash();
+    let advertiser: PeerSocketAddr = ADVERTISER.parse().expect("hard-coded address is valid");
+
+    assert!(
+        matches!(
+            downloads.download_and_verify(hash, Some(advertiser)),
+            DownloadAction::AddedToQueue
+        ),
+        "download is queued"
+    );
+
+    state
+        .expect_request(zs::Request::KnownBlock(hash))
+        .await
+        .respond(zs::Response::KnownBlock(None));
+
+    network
+        .expect_request(zn::Request::BlocksByHash(iter::once(hash).collect()))
+        .await
+        .respond(zn::Response::Blocks(vec![Available((
+            block.clone(),
+            Some(advertiser),
+        ))]));
+
+    // The parent lookup is deliberately never answered, so it can only end by timing out.
+    let (error, advertiser_addr) = downloads
+        .next()
+        .await
+        .expect("downloads is non-empty")
+        .expect_err("block behind the reorg limit is dropped");
+
+    assert!(
+        matches!(
+            error.downcast_ref::<HeightLimitError>(),
+            Some(HeightLimitError::BehindTip { .. })
+        ),
+        "a timed-out lookup must still drop with a typed error, but was: {error:?}"
+    );
+    assert_eq!(
+        advertiser_addr, None,
+        "a timed-out parent lookup must not attribute the drop"
+    );
+
+    verifier.expect_no_requests().await;
+}
+
+/// A block at the oldest height that is still within the reorg limit is verified, not dropped.
+///
+/// This is the guard against dropping and attributing honest near-boundary blocks:
+/// `min_accepted_height` is the boundary, and the behind-tip comparison is strict, so a block
+/// exactly on it is a normal download and the parent is never consulted.
+#[tokio::test]
+async fn block_at_reorg_boundary_is_verified_not_dropped() {
+    let _init_guard = zebra_test::init();
+
+    // `min_accepted_height` is `Height(1)`, so the height-1 block sits exactly on the boundary.
+    let (mut downloads, mut network, mut verifier, mut state) =
+        mock_downloads(Height(MAX_BLOCK_REORG_HEIGHT + 1));
+
+    let block = block_1();
+    let hash = block.hash();
+    let advertiser: PeerSocketAddr = ADVERTISER.parse().expect("hard-coded address is valid");
+
+    assert!(
+        matches!(
+            downloads.download_and_verify(hash, Some(advertiser)),
+            DownloadAction::AddedToQueue
+        ),
+        "download is queued"
+    );
+
+    state
+        .expect_request(zs::Request::KnownBlock(hash))
+        .await
+        .respond(zs::Response::KnownBlock(None));
+
+    network
+        .expect_request(zn::Request::BlocksByHash(iter::once(hash).collect()))
+        .await
+        .respond(zn::Response::Blocks(vec![Available((
+            block.clone(),
+            Some(advertiser),
+        ))]));
+
+    verifier
+        .expect_request(zebra_consensus::Request::Commit(block))
+        .await
+        .respond(hash);
+
+    assert_eq!(
+        downloads
+            .next()
+            .await
+            .expect("downloads is non-empty")
+            .expect("block on the reorg boundary is verified"),
+        hash,
+        "a block at min_accepted_height must be verified, not dropped as behind the tip"
+    );
+
+    // The parent lookup only runs on the behind-tip drop path, so a boundary block must not trigger
+    // one.
+    state.expect_no_requests().await;
+}
+
+/// The far-ahead sibling of the regression test for GHSA-4f6v-mj46-gxg3: a gossiped body whose
+/// claimed height is above the lookahead limit, and contradicts the parent we already hold, is
+/// attributed to the peer that supplied it, and never reaches consensus.
+///
+/// The sync path deliberately leaves its far-ahead drops unscored (GHSA-qhr3-cvch-5fh2), because
+/// the serving peer did not choose the height of a genuine block. Here the parent is the proof, so
+/// scoring is safe: a genuine block whose parent we hold is at most one above the tip, so its real
+/// height is never far ahead.
+#[tokio::test]
+async fn contradicted_far_ahead_height_is_attributed_and_never_verified() {
+    let _init_guard = zebra_test::init();
+
+    let (mut downloads, mut network, mut verifier, mut state) =
+        mock_downloads(lookahead_boundary_tip());
+
+    // Block 2's header with block 10's body: the hash and parent are block 2's, because the hash
+    // covers only the header, but the coinbase now claims height 10 instead of 2.
+    let block_2 = block_2();
+    let block_10 = block_10();
+    let block = Arc::new(Block {
+        header: block_2.header.clone(),
+        transactions: block_10.transactions.clone(),
+    });
+    let hash = block.hash();
+    assert_eq!(
+        hash,
+        block_2.hash(),
+        "the block hash covers only the header"
+    );
+    assert_eq!(
+        block.coinbase_height(),
+        Some(Height(10)),
+        "the body must claim the height the downloader reads"
+    );
+
+    let advertiser: PeerSocketAddr = ADVERTISER.parse().expect("hard-coded address is valid");
+
+    assert!(
+        matches!(
+            downloads.download_and_verify(hash, Some(advertiser)),
+            DownloadAction::AddedToQueue
+        ),
+        "download is queued"
+    );
+
+    state
+        .expect_request(zs::Request::KnownBlock(hash))
+        .await
+        .respond(zs::Response::KnownBlock(None));
+
+    network
+        .expect_request(zn::Request::BlocksByHash(iter::once(hash).collect()))
+        .await
+        .respond(zn::Response::Blocks(vec![Available((
+            block.clone(),
+            Some(advertiser),
+        ))]));
+
+    // We hold the real parent, block 1, so the body's real height is 2, not the 10 it claims.
+    let block_1 = block_1();
+    state
+        .expect_request(zs::Request::BlockHeader(
+            block.header.previous_block_hash.into(),
+        ))
+        .await
+        .respond(zs::Response::BlockHeader {
+            header: block_1.header.clone(),
+            hash: block_1.hash(),
+            height: Height(1),
+            next_block_hash: Some(hash),
+        });
+
+    let (error, advertiser_addr) = downloads
+        .next()
+        .await
+        .expect("downloads is non-empty")
+        .expect_err("block above the lookahead limit is dropped");
+
+    assert!(
+        matches!(
+            error.downcast_ref::<HeightLimitError>(),
+            Some(HeightLimitError::AboveLookahead { .. })
+        ),
+        "a contradicted far-ahead height must be a scoreable typed error, but was: {error:?}"
+    );
+    assert_eq!(
+        advertiser_addr,
+        Some(advertiser),
+        "a contradicted far-ahead height must attribute the drop to the supplying peer"
+    );
+
+    verifier.expect_no_requests().await;
+}
+
+/// A peer that serves a genuinely far-ahead block is not attributed, so it cannot be scored.
+///
+/// This is the common case while Zebra is catching up: the block's parent is not in the state yet,
+/// so there is no proof of misbehaviour and the drop must stay anonymous.
+#[tokio::test]
+async fn genuinely_far_ahead_block_is_dropped_without_attribution() {
+    let _init_guard = zebra_test::init();
+
+    let (mut downloads, mut network, mut verifier, mut state) =
+        mock_downloads(lookahead_boundary_tip());
+
+    let block = block_10();
+    let hash = block.hash();
+    let advertiser: PeerSocketAddr = ADVERTISER.parse().expect("hard-coded address is valid");
+
+    assert!(
+        matches!(
+            downloads.download_and_verify(hash, Some(advertiser)),
+            DownloadAction::AddedToQueue
+        ),
+        "download is queued"
+    );
+
+    state
+        .expect_request(zs::Request::KnownBlock(hash))
+        .await
+        .respond(zs::Response::KnownBlock(None));
+
+    network
+        .expect_request(zn::Request::BlocksByHash(iter::once(hash).collect()))
+        .await
+        .respond(zn::Response::Blocks(vec![Available((
+            block.clone(),
+            Some(advertiser),
+        ))]));
+
+    // The parent, block 9, is far ahead too, so we do not hold it.
+    state
+        .expect_request(zs::Request::BlockHeader(
+            block.header.previous_block_hash.into(),
+        ))
+        .await
+        .respond(Err(zn::BoxError::from("block hash or height not found")));
+
+    let (error, advertiser_addr) = downloads
+        .next()
+        .await
+        .expect("downloads is non-empty")
+        .expect_err("block above the lookahead limit is dropped");
+
+    assert!(
+        matches!(
+            error.downcast_ref::<HeightLimitError>(),
+            Some(HeightLimitError::AboveLookahead { .. })
+        ),
+        "a far-ahead drop must be a typed error, but was: {error:?}"
+    );
+    assert_eq!(
+        advertiser_addr, None,
+        "a genuinely far-ahead block must not be attributed to its peer"
+    );
+
+    verifier.expect_no_requests().await;
+}
+
+/// A block at the highest height that is still within the lookahead limit is verified, not dropped.
+///
+/// This is the guard against dropping and attributing honest near-boundary blocks:
+/// `max_lookahead_height` is the boundary, and the far-ahead comparison is strict, so a block exactly
+/// on it is a normal download and the parent is never consulted.
+#[tokio::test]
+async fn block_at_lookahead_boundary_is_verified_not_dropped() {
+    let _init_guard = zebra_test::init();
+
+    let (mut downloads, mut network, mut verifier, mut state) =
+        mock_downloads(lookahead_boundary_tip());
+
+    let block = block_2();
+    let hash = block.hash();
+    let advertiser: PeerSocketAddr = ADVERTISER.parse().expect("hard-coded address is valid");
+
+    assert!(
+        matches!(
+            downloads.download_and_verify(hash, Some(advertiser)),
+            DownloadAction::AddedToQueue
+        ),
+        "download is queued"
+    );
+
+    state
+        .expect_request(zs::Request::KnownBlock(hash))
+        .await
+        .respond(zs::Response::KnownBlock(None));
+
+    network
+        .expect_request(zn::Request::BlocksByHash(iter::once(hash).collect()))
+        .await
+        .respond(zn::Response::Blocks(vec![Available((
+            block.clone(),
+            Some(advertiser),
+        ))]));
+
+    verifier
+        .expect_request(zebra_consensus::Request::Commit(block))
+        .await
+        .respond(hash);
+
+    assert_eq!(
+        downloads
+            .next()
+            .await
+            .expect("downloads is non-empty")
+            .expect("block on the lookahead boundary is verified"),
+        hash,
+        "a block at max_lookahead_height must be verified, not dropped as far ahead"
+    );
+
+    // The parent lookup only runs on the height limit drop paths, so a boundary block must not
+    // trigger one.
+    state.expect_no_requests().await;
+}
```

### zebrad/src/components/inbound/tests/fake_peer_set.rs
```diff
@@ -30,12 +30,18 @@ use zebra_network::{
 };
 use zebra_node_services::mempool;
 use zebra_rpc::SubmitBlockChannel;
-use zebra_state::{ChainTipChange, Config as StateConfig, CHAIN_TIP_UPDATE_WAIT_LIMIT};
+use zebra_state::{
+    ChainTipBlock, ChainTipChange, ChainTipSender, CheckpointVerifiedBlock, Config as StateConfig,
+    LatestChainTip, CHAIN_TIP_UPDATE_WAIT_LIMIT,
+};
 use zebra_test::mock_service::{MockService, PanicAssertion};
 
 use crate::{
     components::{
-        inbound::{downloads::MAX_INBOUND_CONCURRENCY, Inbound, InboundSetupData},
+        inbound::{
+            downloads::{HeightLimitError, MAX_INBOUND_CONCURRENCY},
+            Inbound, InboundSetupData,
+        },
         mempool::{
             gossip_mempool_transaction_id, Config as MempoolConfig, Mempool, MempoolError,
             SameEffectsChainRejectionError, UnboxMempoolError,
@@ -1229,6 +1235,33 @@ async fn setup_gossiped_block_misbehavior(
     let network = Mainnet;
     let state_config = StateConfig::ephemeral();
 
+    // An empty state, so gossiped blocks are always unknown, and the lookahead limit is
+    // measured from the genesis height.
+    let (state, _read_only_state_service, latest_chain_tip, _chain_tip_change) =
+        zebra_state::init(state_config, &network, Height::MAX, 0).await;
+    let state_service = ServiceBuilder::new().buffer(1).service(state);
+
+    setup_gossiped_block_misbehavior_with_state(block_verifier, state_service, latest_chain_tip)
+        .await
+}
+
+/// The buffered state service type the [`Inbound`] service is wired with in production.
+type StateService =
+    Buffer<BoxService<zebra_state::Request, zebra_state::Response, BoxError>, zebra_state::Request>;
+
+/// Like [`setup_gossiped_block_misbehavior`], but with the given `state` and `latest_chain_tip`, so
+/// a test can pre-populate the state, or report a chain tip of its choosing.
+async fn setup_gossiped_block_misbehavior_with_state(
+    block_verifier: SemanticBlockVerifierStub,
+    state_service: StateService,
+    latest_chain_tip: LatestChainTip,
+) -> (
+    Inbound,
+    MockService<Request, Response, PanicAssertion>,
+    tokio::sync::mpsc::Receiver<(PeerSocketAddr, u32)>,
+) {
+    let network = Mainnet;
+
     let address_book = AddressBook::new(
         SocketAddr::from_str("0.0.0.0:0").unwrap(),
         &network,
@@ -1237,12 +1270,6 @@ async fn setup_gossiped_block_misbehavior(
     );
     let address_book = Arc::new(std::sync::Mutex::new(address_book));
 
-    // An empty state, so gossiped blocks are always unknown, and the lookahead limit is
-    // measured from the genesis height.
-    let (state, _read_only_state_service, latest_chain_tip, _chain_tip_change) =
-        zebra_state::init(state_config, &network, Height::MAX, 0).await;
-    let state_service = ServiceBuilder::new().buffer(1).service(state);
-
     let peer_set = MockService::build()
         .with_max_request_delay(MAX_PEER_SET_REQUEST_DELAY)
         .for_unit_tests();
@@ -1536,3 +1563,256 @@ async fn gossiped_block_verify_timeout_does_not_score_serving_peer() -> Result<(
 
     Ok(())
 }
+
+/// A real state holding the mainnet genesis block and block 1, with its linked chain tip at height 1.
+///
+/// The height limit tests gossip block 2's header, so the download task can look up block 1 as its
+/// parent, and use its height to decide whether the body's claimed height was rewritten.
+async fn state_holding_genesis_and_block_1() -> (StateService, LatestChainTip) {
+    let blocks: [&[u8]; 2] = [
+        &zebra_test::vectors::BLOCK_MAINNET_GENESIS_BYTES,
+        &zebra_test::vectors::BLOCK_MAINNET_1_BYTES,
+    ];
+    let blocks = blocks.into_iter().map(|bytes| {
+        bytes
+            .zcash_deserialize_into::<Arc<Block>>()
+            .expect("hard-coded block vector deserializes")
+    });
+
+    let (state, _read_only_state_service, latest_chain_tip, _chain_tip_change) =
+        zebra_state::populated_state(blocks, &Mainnet).await;
+
+    (state, latest_chain_tip)
+}
+
+/// A chain tip far enough past the reorg limit that a claimed height of 1 is behind the finalized
+/// tip, without committing a hundred blocks to the state.
+///
+/// The state keeps holding block 1, exactly as it would if it had kept syncing, so the download task
+/// can still prove a rewritten height against it. Tests keep the returned sender alive for their whole
+/// run, so the tip is fixed while they run.
+fn far_ahead_chain_tip() -> (ChainTipSender, LatestChainTip) {
+    let tip_block: Arc<Block> = zebra_test::vectors::BLOCK_MAINNET_982681_BYTES
+        .zcash_deserialize_into()
+        .expect("hard-coded block vector deserializes");
+    assert!(
+        tip_block
+            .coinbase_height()
+            .expect("block vector has a height")
+            > Height(zebra_state::MAX_BLOCK_REORG_HEIGHT + 1),
+        "the fake tip must put height 1 behind the reorg limit"
+    );
+
+    let (chain_tip_sender, latest_chain_tip, _chain_tip_change) = ChainTipSender::new(
+        ChainTipBlock::from(CheckpointVerifiedBlock::from(tip_block)),
+        &Mainnet,
+    );
+
+    (chain_tip_sender, latest_chain_tip)
+}
+
+/// A stub semantic block verifier that records every request on the returned channel, and fails it
+/// with a benign error, so the height limit tests can check that a dropped block never reached it.
+fn recording_block_verifier() -> (SemanticBlockVerifierStub, tokio::sync::mpsc::Receiver<()>) {
+    let (verifier_called_tx, verifier_called_rx) = tokio::sync::mpsc::channel(1);
+
+    let block_verifier = Buffer::new(
+        BoxService::new(tower::service_fn(move |_req: zebra_consensus::Request| {
+            let verifier_called_tx = verifier_called_tx.clone();
+            async move {
+                let _ = verifier_called_tx.try_send(());
+                Err::<zebra_chain::block::Hash, RouterError>(RouterError::Block {
+                    source: Box::new(VerifyBlockError::ValidateProposal(
+                        "the height limit tests must drop blocks before verification".into(),
+                    )),
+                })
+            }
+        })),
+        10,
+    );
+
+    (block_verifier, verifier_called_rx)
+}
+
+/// Block 2's header with `body`'s transactions: the hash and parent are block 2's, because the hash
+/// covers only the header, but the coinbase claims `body`'s height.
+///
+/// This is the shape of the GHSA-4f6v-mj46-gxg3 attack, without reproducing the hash-preserving
+/// coinbase rewrite itself.
+fn block_2_header_with_body(body: &Block) -> Arc<Block> {
+    let block_2: Arc<Block> = zebra_test::vectors::BLOCK_MAINNET_2_BYTES
+        .zcash_deserialize_into()
+        .expect("hard-coded block vector deserializes");
+
+    let block = Arc::new(Block {
+        header: block_2.header.clone(),
+        transactions: body.transactions.clone(),
+    });
+    assert_eq!(
+        block.hash(),
+        block_2.hash(),
+        "the block hash covers only the header"
+    );
+    assert_eq!(
+        block.coinbase_height(),
+        body.coinbase_height(),
+        "the body must claim the height the downloader reads"
+    );
+
+    block
+}
+
+/// A peer that serves a gossiped block whose coinbase height was rewritten to fall behind the
+/// finalized tip must have its misbehaviour score raised, when the parent Zebra holds proves the
+/// rewrite.
+///
+/// The download task drops the block before it reaches the verifier, so the verifier can never score
+/// the peer: the drop itself must carry the score through the cleanup loop in
+/// `Inbound::poll_ready()`, like a verification failure does.
+///
+/// End-to-end regression test for `GHSA-4f6v-mj46-gxg3`; the download stream is unit tested in
+/// `inbound::downloads::tests`.
+#[tokio::test(flavor = "multi_thread")]
+async fn gossiped_block_contradicted_behind_tip_height_scores_serving_peer() -> Result<(), BoxError>
+{
+    let _init_guard = zebra_test::init();
+
+    let advertiser = PeerSocketAddr::from(([192, 168, 180, 14], 10_000));
+    let serving_peer = PeerSocketAddr::from(([192, 168, 180, 15], 10_000));
+
+    // Block 2's header with block 1's body: the coinbase claims height 1, but we hold block 1 as
+    // the parent, so the body's real height is 2.
+    let block_1: Arc<Block> =
+        zebra_test::vectors::BLOCK_MAINNET_1_BYTES.zcash_deserialize_into()?;
+    let block = block_2_header_with_body(&block_1);
+
+    // Derive the expected score, so the test tracks scoring policy changes.
+    let expected_score = HeightLimitError::BehindTip {
+        height: Height(1),
+        hash: block.hash(),
+    }
+    .misbehavior_score();
+    assert_ne!(
+        expected_score, 0,
+        "a parent-proven rewritten height must have a non-zero misbehaviour score",
+    );
+
+    let (state, _linked_chain_tip) = state_holding_genesis_and_block_1().await;
+    let (_chain_tip_sender, latest_chain_tip) = far_ahead_chain_tip();
+    let (block_verifier, mut verifier_called_rx) = recording_block_verifier();
+
+    let (mut inbound, mut peer_set, mut misbehavior_rx) =
+        setup_gossiped_block_misbehavior_with_state(block_verifier, state, latest_chain_tip).await;
+
+    advertise_and_serve_block(&mut inbound, &mut peer_set, block, advertiser, serving_peer).await?;
+
+    let report = poll_for_misbehavior_report(&mut inbound, &mut misbehavior_rx).await;
+
+    assert_eq!(
+        report,
+        Some((serving_peer, expected_score)),
+        "the peer that served a parent-proven rewritten height must be reported for misbehaviour",
+    );
+    assert_eq!(
+        misbehavior_rx.try_recv().ok(),
+        None,
+        "no other peer may be reported for this download",
+    );
+    assert!(
+        verifier_called_rx.try_recv().is_err(),
+        "a block behind the finalized tip must be dropped before consensus validation",
+    );
+
+    Ok(())
+}
+
+/// The far-ahead sibling of the test above: a coinbase height rewritten past the lookahead limit is
+/// scored too, when the parent Zebra holds proves the rewrite.
+///
+/// Here the state's own chain tip is used, at height 1: a genuine block whose parent we hold is at
+/// most one above the tip, so a held parent is proof that a far-ahead height was rewritten.
+#[tokio::test(flavor = "multi_thread")]
+async fn gossiped_block_contradicted_far_ahead_height_scores_serving_peer() -> Result<(), BoxError>
+{
+    let _init_guard = zebra_test::init();
+
+    let advertiser = PeerSocketAddr::from(([192, 168, 180, 16], 10_000));
+    let serving_peer = PeerSocketAddr::from(([192, 168, 180, 17], 10_000));
+
+    // Block 2's header with a body from far above the lookahead limit.
+    let high_block: Arc<Block> =
+        zebra_test::vectors::BLOCK_MAINNET_982681_BYTES.zcash_deserialize_into()?;
+    let claimed_height = high_block
+        .coinbase_height()
+        .expect("block vector has a height");
+    let block = block_2_header_with_body(&high_block);
+
+    let expected_score = HeightLimitError::AboveLookahead {
+        height: claimed_height,
+        hash: block.hash(),
+    }
+    .misbehavior_score();
+    assert_ne!(
+        expected_score, 0,
+        "a parent-proven rewritten height must have a non-zero misbehaviour score",
+    );
+
+    let (state, latest_chain_tip) = state_holding_genesis_and_block_1().await;
+    let (block_verifier, mut verifier_called_rx) = recording_block_verifier();
+
+    let (mut inbound, mut peer_set, mut misbehavior_rx) =
+        setup_gossiped_block_misbehavior_with_state(block_verifier, state, latest_chain_tip).await;
+
+    advertise_and_serve_block(&mut inbound, &mut peer_set, block, advertiser, serving_peer).await?;
+
+    let report = poll_for_misbehavior_report(&mut inbound, &mut misbehavior_rx).await;
+
+    assert_eq!(
+        report,
+        Some((serving_peer, expected_score)),
+        "the peer that served a parent-proven rewritten height must be reported for misbehaviour",
+    );
+    assert!(
+        verifier_called_rx.try_recv().is_err(),
+        "a block above the lookahead limit must be dropped before consensus validation",
+    );
+
+    Ok(())
+}
+
+/// A peer that serves an authentic block from behind the finalized tip must not be scored.
+///
+/// The block is still dropped, but its height agrees with the parent we hold, so there is no proof of
+/// misbehaviour. Negative control for `GHSA-4f6v-mj46-gxg3`: guards against banning honest peers
+/// that serve genuinely old blocks.
+#[tokio::test(flavor = "multi_thread")]
+async fn gossiped_block_genuinely_behind_tip_does_not_score_serving_peer() -> Result<(), BoxError> {
+    let _init_guard = zebra_test::init();
+
+    let peer = PeerSocketAddr::from(([192, 168, 180, 18], 10_000));
+
+    // Block 2 as mined: its coinbase claims height 2, and we hold its parent, block 1.
+    let block: Arc<Block> = zebra_test::vectors::BLOCK_MAINNET_2_BYTES.zcash_deserialize_into()?;
+
+    let (state, _linked_chain_tip) = state_holding_genesis_and_block_1().await;
+    let (_chain_tip_sender, latest_chain_tip) = far_ahead_chain_tip();
+    let (block_verifier, mut verifier_called_rx) = recording_block_verifier();
+
+    let (mut inbound, mut peer_set, mut misbehavior_rx) =
+        setup_gossiped_block_misbehavior_with_state(block_verifier, state, latest_chain_tip).await;
+
+    advertise_and_serve_block(&mut inbound, &mut peer_set, block, peer, peer).await?;
+
+    let report = poll_for_misbehavior_report(&mut inbound, &mut misbehavior_rx).await;
+
+    assert_eq!(
+        report, None,
+        "an authentic block behind the finalized tip must not be reported as peer misbehaviour",
+    );
+    assert!(
+        verifier_called_rx.try_recv().is_err(),
+        "a block behind the finalized tip must be dropped before consensus validation",
+    );
+
+    Ok(())
+}
```
