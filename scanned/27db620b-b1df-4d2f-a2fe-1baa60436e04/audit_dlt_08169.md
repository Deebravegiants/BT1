# [?] fix(inbound): score peers for RouterError from invalid gossiped blocks (GHSA-8hh2-hrf2-cqf4)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-08-05
Source: https://github.com/ZcashFoundation/zebra/commit/356218e5b0daa7cadbe86cc73cfce49e93ccdaf8
Type: security-commit

## Details
fix(inbound): score peers for RouterError from invalid gossiped blocks (GHSA-8hh2-hrf2-cqf4)

## Patch
### CHANGELOG.md
```diff
@@ -68,6 +68,11 @@ and this project adheres to [Semantic Versioning](https://semver.org).
   malicious `FindBlocks` responder get honest peers banned during initial block
   download (GHSA-qhr3-cvch-5fh2)
 
+- Peers that gossip consensus-invalid blocks are scored for misbehavior again. The inbound
+  download cleanup only recognized `VerifyBlockError`, but the gossiped block verifier is a
+  `BlockVerifierRouter`, which returns `RouterError`, so no score was ever applied and such
+  peers were never banned (GHSA-8hh2-hrf2-cqf4)
+
 ## [Zebra 6.2.3](https://github.com/ZcashFoundation/zebra/releases/tag/v6.2.3) - 2026-07-27
 
 This is an optional release with network hardenings for operators that experience issues with their nodes peer set connectivity or otherwise want to be proactive about avoiding such issues.
```

### zebrad/src/components/inbound.rs
```diff
@@ -335,13 +335,29 @@ impl Service<zn::Request> for Inbound {
                         continue;
                     };
 
-                    let Ok(err) = err.downcast::<VerifyBlockError>() else {
+                    // # Security
+                    //
+                    // The gossiped block verifier is a `BlockVerifierRouter`, so a failed
+                    // verification is boxed as a `RouterError`. `Box<dyn Error>::downcast`
+                    // is an exact type match, so downcasting to `VerifyBlockError` alone
+                    // never matched, and misbehaving peers were never scored.
+                    // (`VerifyBlockError` only appears nested inside `RouterError::Block`.)
+                    //
+                    // `VerifyBlockError` is still handled, so scoring keeps working if the
+                    // verifier stack is ever rewired to skip the router.
+                    //
+                    // Any other error (a tower `Elapsed` timeout, a transport failure) is a
+                    // local problem rather than peer misbehavior, so it stays unscored.
+                    let score = if let Some(err) = err.downcast_ref::<RouterError>() {
+                        err.misbehavior_score()
+                    } else if let Some(err) = err.downcast_ref::<VerifyBlockError>() {
+                        err.misbehavior_score()
+                    } else {
                         continue;
                     };
 
-                    if err.misbehavior_score() != 0 {
-                        let _ =
-                            misbehavior_sender.try_send((advertiser_addr, err.misbehavior_score()));
+                    if score != 0 {
+                        let _ = misbehavior_sender.try_send((advertiser_addr, score));
                     }
                 }
 
```

### zebrad/src/components/inbound/tests/fake_peer_set.rs
```diff
@@ -17,7 +17,10 @@ use zebra_chain::{
     serialization::{DateTime32, ZcashDeserializeInto},
     transaction::{UnminedTx, UnminedTxId, VerifiedUnminedTx},
 };
-use zebra_consensus::{error::TransactionError, transaction, Config as ConsensusConfig};
+use zebra_consensus::{
+    error::TransactionError, router::RouterError, transaction, Config as ConsensusConfig,
+    VerifyBlockError,
+};
 use zebra_network::{
     constants::{
         ADDR_RESPONSE_LIMIT_DENOMINATOR, DEFAULT_MAX_CONNS_PER_IP, MAX_ADDRS_IN_ADDRESS_BOOK,
@@ -37,7 +40,7 @@ use crate::{
             gossip_mempool_transaction_id, Config as MempoolConfig, Mempool, MempoolError,
             SameEffectsChainRejectionError, UnboxMempoolError,
         },
-        sync::{self, BlockGossipError, SyncStatus, PEER_GOSSIP_DELAY},
+        sync::{self, BlockGossipError, SyncStatus, BLOCK_VERIFY_TIMEOUT, PEER_GOSSIP_DELAY},
     },
     BoxError,
 };
@@ -1198,3 +1201,338 @@ fn add_some_stuff_to_mempool(
 
     vec![last_transaction]
 }
+
+/// The semantic block verifier type the [`Inbound`] service is wired with in production.
+///
+/// The concrete service inside the [`BoxService`] is a
+/// [`zebra_consensus::router::BlockVerifierRouter`], so its error type is
+/// [`RouterError`] — a bare [`VerifyBlockError`] never escapes this stack, it only
+/// ever appears nested inside [`RouterError::Block`].
+type SemanticBlockVerifierStub = Buffer<
+    BoxService<zebra_consensus::Request, zebra_chain::block::Hash, RouterError>,
+    zebra_consensus::Request,
+>;
+
+/// Wires up an [`Inbound`] service with a stub semantic block verifier, using the same
+/// service types as production, and returns the misbehaviour report receiver.
+///
+/// Unlike the other tests in this module, the returned receiver is *retained* by the
+/// caller, so misbehaviour reports emitted by the gossiped block download cleanup loop
+/// can be asserted on. See `GHSA-8hh2-hrf2-cqf4`.
+async fn setup_gossiped_block_misbehavior(
+    block_verifier: SemanticBlockVerifierStub,
+) -> (
+    Inbound,
+    MockService<Request, Response, PanicAssertion>,
+    tokio::sync::mpsc::Receiver<(PeerSocketAddr, u32)>,
+) {
+    let network = Mainnet;
+    let state_config = StateConfig::ephemeral();
+
+    let address_book = AddressBook::new(
+        SocketAddr::from_str("0.0.0.0:0").unwrap(),
+        &network,
+        DEFAULT_MAX_CONNS_PER_IP,
+        Span::none(),
+    );
+    let address_book = Arc::new(std::sync::Mutex::new(address_book));
+
+    // An empty state, so gossiped blocks are always unknown, and the lookahead limit is
+    // measured from the genesis height.
+    let (state, _read_only_state_service, latest_chain_tip, _chain_tip_change) =
+        zebra_state::init(state_config, &network, Height::MAX, 0).await;
+    let state_service = ServiceBuilder::new().buffer(1).service(state);
+
+    let peer_set = MockService::build()
+        .with_max_request_delay(MAX_PEER_SET_REQUEST_DELAY)
+        .for_unit_tests();
+    let buffered_peer_set = Buffer::new(BoxService::new(peer_set.clone()), 10);
+
+    let mempool_service: MockService<mempool::Request, mempool::Response, PanicAssertion> =
+        MockService::build().for_unit_tests();
+    let buffered_mempool = Buffer::new(BoxService::new(mempool_service), 10);
+
+    let (setup_tx, setup_rx) = oneshot::channel();
+
+    // The `Inbound` service is used directly, without a `Buffer` or `load_shed` wrapper,
+    // so the test can drive `poll_ready()` — and therefore the download cleanup loop —
+    // deterministically.
+    let inbound = Inbound::new(MAX_INBOUND_CONCURRENCY, setup_rx);
+
+    let (misbehavior_sender, misbehavior_rx) = tokio::sync::mpsc::channel(10);
+
+    let setup_data = InboundSetupData {
+        address_book,
+        block_download_peer_set: buffered_peer_set,
+        block_verifier,
+        mempool: buffered_mempool,
+        state: state_service,
+        latest_chain_tip,
+        misbehavior_sender,
+    };
+    let r = setup_tx.send(setup_data);
+    // We can't expect or unwrap because the returned Result does not implement Debug.
+    assert!(r.is_ok(), "unexpected setup channel send failure");
+
+    (inbound, peer_set, misbehavior_rx)
+}
+
+/// Repeatedly polls the [`Inbound`] service, so its gossiped block download cleanup loop
+/// drains any finished downloads, and returns the first misbehaviour report, if any.
+async fn poll_for_misbehavior_report(
+    inbound: &mut Inbound,
+    misbehavior_rx: &mut tokio::sync::mpsc::Receiver<(PeerSocketAddr, u32)>,
+) -> Option<(PeerSocketAddr, u32)> {
+    for _ in 0..60 {
+        let _ = std::future::poll_fn(|cx| inbound.poll_ready(cx)).await;
+
+        if let Ok(report) = misbehavior_rx.try_recv() {
+            return Some(report);
+        }
+
+        tokio::time::sleep(Duration::from_millis(50)).await;
+    }
+
+    None
+}
+
+/// Sends the gossiped block advertisement, and serves the block to the download task.
+///
+/// The advertisement is attributed to `advertiser`, and the `Blocks` response to
+/// `serving_peer` — the address a misbehaviour report is attached to.
+async fn advertise_and_serve_block(
+    inbound: &mut Inbound,
+    peer_set: &mut MockService<Request, Response, PanicAssertion>,
+    block: Arc<Block>,
+    advertiser: PeerSocketAddr,
+    serving_peer: PeerSocketAddr,
+) -> Result<(), BoxError> {
+    let hash = block.hash();
+
+    let response = inbound
+        .ready()
+        .await?
+        .call(Request::AdvertiseBlock(hash, Some(advertiser)))
+        .await?;
+    assert_eq!(
+        response,
+        Response::Nil,
+        "`AdvertiseBlock` requests should always respond `Ok(Nil)`",
+    );
+
+    peer_set
+        .expect_request(Request::BlocksByHash(iter::once(hash).collect()))
+        .await
+        .respond(Response::Blocks(vec![Available((
+            block,
+            Some(serving_peer),
+        ))]));
+
+    Ok(())
+}
+
+/// The [`RouterError`] served by the misbehaving stub verifier: a misbehaviour-scoring
+/// consensus failure, wrapped exactly like the router wraps it.
+fn invalid_gossiped_block_router_error() -> RouterError {
+    RouterError::Block {
+        source: Box::new(VerifyBlockError::Subsidy(
+            zebra_chain::parameters::subsidy::SubsidyError::NoCoinbase,
+        )),
+    }
+}
+
+/// A peer that serves a consensus-invalid gossiped block must have its misbehaviour score
+/// raised.
+///
+/// The production inbound block verifier is a `BlockVerifierRouter`, so a failed
+/// verification is boxed as a [`RouterError`]. The cleanup loop in `Inbound::poll_ready()`
+/// downcast the boxed error to [`VerifyBlockError`] instead, and `Box<dyn Error>::downcast`
+/// is an exact `TypeId` match, so the downcast always failed and no peer was ever scored
+/// for serving an invalid gossiped block.
+///
+/// Note that this test *retains* the misbehaviour receiver. Every other test in this module
+/// drops it, which is why the bug went unnoticed.
+///
+/// Regression test for `GHSA-8hh2-hrf2-cqf4`.
+#[tokio::test(flavor = "multi_thread")]
+async fn gossiped_block_router_error_scores_serving_peer() -> Result<(), BoxError> {
+    let _init_guard = zebra_test::init();
+
+    let block: Arc<Block> = zebra_test::vectors::BLOCK_MAINNET_1_BYTES.zcash_deserialize_into()?;
+    let peer = PeerSocketAddr::from(([192, 168, 180, 9], 10_000));
+
+    // Derive the expected score, so the test tracks scoring policy changes. If the sample
+    // error's score ever drops to zero, the guard fails loudly instead of the report
+    // assertion becoming vacuous.
+    let expected_score = invalid_gossiped_block_router_error().misbehavior_score();
+    assert_ne!(
+        expected_score, 0,
+        "the test error must have a non-zero misbehaviour score",
+    );
+
+    let block_verifier = Buffer::new(
+        BoxService::new(tower::service_fn(|_req: zebra_consensus::Request| async {
+            Err::<zebra_chain::block::Hash, RouterError>(invalid_gossiped_block_router_error())
+        })),
+        10,
+    );
+
+    let (mut inbound, mut peer_set, mut misbehavior_rx) =
+        setup_gossiped_block_misbehavior(block_verifier).await;
+
+    advertise_and_serve_block(&mut inbound, &mut peer_set, block, peer, peer).await?;
+
+    let report = poll_for_misbehavior_report(&mut inbound, &mut misbehavior_rx).await;
+
+    assert_eq!(
+        report,
+        Some((peer, expected_score)),
+        "a peer that serves a consensus-invalid gossiped block must be reported for misbehaviour",
+    );
+
+    Ok(())
+}
+
+/// The misbehaviour report is attached to the peer that served the invalid block, not to
+/// the advertiser that announced it: the download task takes the reported address from the
+/// `Blocks` response, which is set by the connection that actually delivered the bytes.
+#[tokio::test(flavor = "multi_thread")]
+async fn gossiped_block_scores_serving_peer_not_advertiser() -> Result<(), BoxError> {
+    let _init_guard = zebra_test::init();
+
+    let block: Arc<Block> = zebra_test::vectors::BLOCK_MAINNET_1_BYTES.zcash_deserialize_into()?;
+    let advertiser = PeerSocketAddr::from(([192, 168, 180, 12], 10_000));
+    let serving_peer = PeerSocketAddr::from(([192, 168, 180, 13], 10_000));
+
+    let expected_score = invalid_gossiped_block_router_error().misbehavior_score();
+    assert_ne!(
+        expected_score, 0,
+        "the test error must have a non-zero misbehaviour score",
+    );
+
+    let block_verifier = Buffer::new(
+        BoxService::new(tower::service_fn(|_req: zebra_consensus::Request| async {
+            Err::<zebra_chain::block::Hash, RouterError>(invalid_gossiped_block_router_error())
+        })),
+        10,
+    );
+
+    let (mut inbound, mut peer_set, mut misbehavior_rx) =
+        setup_gossiped_block_misbehavior(block_verifier).await;
+
+    advertise_and_serve_block(&mut inbound, &mut peer_set, block, advertiser, serving_peer).await?;
+
+    let report = poll_for_misbehavior_report(&mut inbound, &mut misbehavior_rx).await;
+
+    assert_eq!(
+        report,
+        Some((serving_peer, expected_score)),
+        "the peer that served the invalid block must be scored, not the advertiser",
+    );
+    assert_eq!(
+        misbehavior_rx.try_recv().ok(),
+        None,
+        "no other peer may be reported for this download",
+    );
+
+    Ok(())
+}
+
+/// A verification failure that is not peer misbehaviour must not raise any score.
+///
+/// Guards against over-banning after the `GHSA-8hh2-hrf2-cqf4` fix: only errors whose
+/// `misbehavior_score()` is non-zero may be reported.
+#[tokio::test(flavor = "multi_thread")]
+async fn gossiped_block_benign_router_error_does_not_score_serving_peer() -> Result<(), BoxError> {
+    let _init_guard = zebra_test::init();
+
+    let block: Arc<Block> = zebra_test::vectors::BLOCK_MAINNET_1_BYTES.zcash_deserialize_into()?;
+    let peer = PeerSocketAddr::from(([192, 168, 180, 10], 10_000));
+
+    // `VerifyBlockError::ValidateProposal` has a misbehaviour score of zero.
+    let block_verifier = Buffer::new(
+        BoxService::new(tower::service_fn(|_req: zebra_consensus::Request| async {
+            Err::<zebra_chain::block::Hash, RouterError>(RouterError::Block {
+                source: Box::new(VerifyBlockError::ValidateProposal(
+                    "not peer misbehaviour".into(),
+                )),
+            })
+        })),
+        10,
+    );
+
+    let (mut inbound, mut peer_set, mut misbehavior_rx) =
+        setup_gossiped_block_misbehavior(block_verifier).await;
+
+    advertise_and_serve_block(&mut inbound, &mut peer_set, block, peer, peer).await?;
+
+    let report = poll_for_misbehavior_report(&mut inbound, &mut misbehavior_rx).await;
+
+    assert_eq!(
+        report, None,
+        "a verification failure with a zero misbehaviour score must not be reported",
+    );
+
+    Ok(())
+}
+
+/// A block verification timeout must not raise the serving peer's misbehaviour score.
+///
+/// The inbound verifier is wrapped in a tower [`tower::timeout::Timeout`], so a slow
+/// verification produces a boxed `tower::timeout::error::Elapsed`, not a [`RouterError`].
+/// That is a local failure, not evidence that the peer misbehaved.
+///
+/// Negative control for `GHSA-8hh2-hrf2-cqf4`.
+#[tokio::test]
+async fn gossiped_block_verify_timeout_does_not_score_serving_peer() -> Result<(), BoxError> {
+    let _init_guard = zebra_test::init();
+
+    let block: Arc<Block> = zebra_test::vectors::BLOCK_MAINNET_1_BYTES.zcash_deserialize_into()?;
+    let peer = PeerSocketAddr::from(([192, 168, 180, 11], 10_000));
+
+    // Signals that the download task has reached the verifier, and is now parked inside
+    // the `Timeout` layer.
+    let (verifier_called_tx, mut verifier_called_rx) = tokio::sync::mpsc::channel(1);
+
+    let block_verifier = Buffer::new(
+        BoxService::new(tower::service_fn(move |_req: zebra_consensus::Request| {
+            let verifier_called_tx = verifier_called_tx.clone();
+            async move {
+                let _ = verifier_called_tx.send(()).await;
+                std::future::pending::<Result<zebra_chain::block::Hash, RouterError>>().await
+            }
+        })),
+        10,
+    );
+
+    let (mut inbound, mut peer_set, mut misbehavior_rx) =
+        setup_gossiped_block_misbehavior(block_verifier).await;
+
+    advertise_and_serve_block(&mut inbound, &mut peer_set, block.clone(), peer, peer).await?;
+
+    verifier_called_rx
+        .recv()
+        .await
+        .expect("the download task should reach the block verifier");
+
+    // Fast-forward past the verification timeout, so tower's `Timeout` layer produces a
+    // real `Elapsed` error at exactly the position a `RouterError` would appear.
+    tokio::time::pause();
+    tokio::time::advance(BLOCK_VERIFY_TIMEOUT + Duration::from_secs(1)).await;
+    tokio::time::resume();
+
+    let report = poll_for_misbehavior_report(&mut inbound, &mut misbehavior_rx).await;
+
+    assert_eq!(
+        report, None,
+        "a block verification timeout must not be reported as peer misbehaviour",
+    );
+
+    // Make sure the assertion above isn't vacuous: the timed-out download must actually
+    // have been drained by the cleanup loop. If it were still in flight, the per-IP and
+    // per-hash caps would drop this second advertisement, and no `BlocksByHash` request
+    // would reach the peer set.
+    advertise_and_serve_block(&mut inbound, &mut peer_set, block, peer, peer).await?;
+
+    Ok(())
+}
```
