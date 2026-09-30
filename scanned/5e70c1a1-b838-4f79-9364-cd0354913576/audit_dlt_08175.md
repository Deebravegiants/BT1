# [?] test(mempool): regression test for pushed-tx misbehavior attribution gap (GHSA-g7c4-2w6c-cr3r)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-07-16
Source: https://github.com/ZcashFoundation/zebra/commit/96d95be0041f0ff9da8b35074ebcd7bdcb8e9b36
Type: security-commit

## Details
test(mempool): regression test for pushed-tx misbehavior attribution gap (GHSA-g7c4-2w6c-cr3r)

Co-Authored-By: evan-forbes <evan.samuel.forbes@gmail.com>

## Patch
### zebrad/src/components/mempool/downloads/tests.rs
```diff
@@ -1,5 +1,10 @@
 //! Fixed test vectors for the mempool transaction downloader.
 
+use std::time::Duration;
+
+use futures::StreamExt as _;
+use tower::{service_fn, util::BoxCloneService};
+
 use zebra_chain::parameters::Network;
 use zebra_test::mock_service::{MockService, PanicAssertion};
 
@@ -63,3 +68,63 @@ async fn per_peer_cap_applies_to_pushed_transactions() {
     // Don't leave spawned download tasks behind when the runtime shuts down.
     downloads.cancel_all();
 }
+
+/// A directly pushed transaction from a peer must keep that peer's address on
+/// the `Invalid` verification error, so the mempool can score the peer's
+/// misbehavior. Regression test for `GHSA-g7c4-2w6c-cr3r`.
+#[tokio::test]
+async fn pushed_transaction_attributes_invalid_error_to_peer() {
+    use zebra_consensus::error::TransactionError;
+
+    let _init_guard = zebra_test::init();
+
+    let network = Network::Mainnet;
+    let peer_addr: SocketAddr = "203.0.113.7:8233".parse().unwrap();
+    let transaction = network
+        .unmined_transactions_in_blocks(1..=1)
+        .next()
+        .expect("at least one test transaction")
+        .transaction;
+
+    type BoxError = Box<dyn std::error::Error + Send + Sync + 'static>;
+
+    let mut downloads = Downloads::new(
+        BoxCloneService::new(service_fn(|_request| async move {
+            panic!("pushed transactions must not be downloaded");
+        })),
+        BoxCloneService::new(service_fn(|_request| async move {
+            Err(Box::new(TransactionError::WrongVersion) as BoxError)
+        })),
+        BoxCloneService::new(service_fn(|request| async move {
+            match request {
+                zs::Request::Transaction(_) => Ok(zs::Response::Transaction(None)),
+                zs::Request::Tip => Ok(zs::Response::Tip(None)),
+                request => Err(format!("unexpected state request: {request:?}").into()),
+            }
+        })),
+    );
+
+    downloads
+        .download_if_needed_and_verify(Gossip::Tx(transaction), Some(peer_addr), None)
+        .expect("download is queued");
+
+    let result = tokio::time::timeout(Duration::from_secs(1), downloads.next())
+        .await
+        .expect("pushed transaction should complete")
+        .expect("download stream should yield an item")
+        .expect("pushed transaction should not time out");
+
+    let error = result
+        .expect_err("invalid pushed transaction should fail verification")
+        .1;
+    assert!(
+        matches!(
+            error,
+            TransactionDownloadVerifyError::Invalid {
+                advertiser_addr: Some(addr),
+                ..
+            } if addr == PeerSocketAddr::from(peer_addr)
+        ),
+        "expected the pushed transaction failure to carry the peer address, got {error:?}"
+    );
+}
```
