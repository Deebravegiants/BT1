# [?] test(inbound): add failing regression test for GHSA-8hh2-hrf2-cqf4 gossip misbehavior scoring

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-08-03
Source: https://github.com/ZcashFoundation/zebra/commit/78fa95b6955c882fba6f95ae007dd59c8505cd90
Type: security-commit

## Details
test(inbound): add failing regression test for GHSA-8hh2-hrf2-cqf4 gossip misbehavior scoring

## Patch
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
@@ -1198,3 +1201,272 @@ fn add_some_stuff_to_mempool(
 
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
+async fn advertise_and_serve_block(
+    inbound: &mut Inbound,
+    peer_set: &mut MockService<Request, Response, PanicAssertion>,
+    block: Arc<Block>,
+    peer: PeerSocketAddr,
+) -> Result<(), BoxError> {
+    let hash = block.hash();
+
+    let response = inbound
+        .ready()
+        .await?
+        .call(Request::AdvertiseBlock(hash, Some(peer)))
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
+        .respond(Response::Blocks(vec![Available((block, Some(peer)))]));
+
+    Ok(())
+}
+
+/// A peer that gossips a consensus-invalid block must have its misbehaviour score raised.
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
+async fn gossiped_block_router_error_scores_advertising_peer() -> Result<(), BoxError> {
+    let _init_guard = zebra_test::init();
+
+    let block: Arc<Block> = zebra_test::vectors::BLOCK_MAINNET_1_BYTES.zcash_deserialize_into()?;
+    let peer = PeerSocketAddr::from(([192, 168, 180, 9], 10_000));
+
+    // A misbehaviour-scoring consensus failure, wrapped exactly like the router wraps it.
+    let block_verifier = Buffer::new(
+        BoxService::new(tower::service_fn(|_req: zebra_consensus::Request| async {
+            Err::<zebra_chain::block::Hash, RouterError>(RouterError::Block {
+                source: Box::new(VerifyBlockError::Subsidy(
+                    zebra_chain::parameters::subsidy::SubsidyError::NoCoinbase,
+                )),
+            })
+        })),
+        10,
+    );
+
+    let (mut inbound, mut peer_set, mut misbehavior_rx) =
+        setup_gossiped_block_misbehavior(block_verifier).await;
+
+    advertise_and_serve_block(&mut inbound, &mut peer_set, block, peer).await?;
+
+    let report = poll_for_misbehavior_report(&mut inbound, &mut misbehavior_rx).await;
+
+    assert_eq!(
+        report,
+        Some((peer, 100)),
+        "a peer that gossips a consensus-invalid block must be reported for misbehaviour",
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
+async fn gossiped_block_benign_router_error_does_not_score_advertising_peer() -> Result<(), BoxError>
+{
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
+    advertise_and_serve_block(&mut inbound, &mut peer_set, block, peer).await?;
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
+/// A block verification timeout must not raise the advertising peer's misbehaviour score.
+///
+/// The inbound verifier is wrapped in a tower [`tower::timeout::Timeout`], so a slow
+/// verification produces a boxed `tower::timeout::error::Elapsed`, not a [`RouterError`].
+/// That is a local failure, not evidence that the peer misbehaved.
+///
+/// Negative control for `GHSA-8hh2-hrf2-cqf4`.
+#[tokio::test]
+async fn gossiped_block_verify_timeout_does_not_score_advertising_peer() -> Result<(), BoxError> {
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
+    advertise_and_serve_block(&mut inbound, &mut peer_set, block.clone(), peer).await?;
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
+    advertise_and_serve_block(&mut inbound, &mut peer_set, block, peer).await?;
+
+    Ok(())
+}
```
