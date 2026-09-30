# [?] Fix panic in evidence serialization (#798)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/tendermint-rs
Published: 2021-02-09
Source: https://github.com/cometbft/tendermint-rs/commit/95bd6da676e1024941e42f654431a72c0ff21aab
Type: security-commit

## Details
Fix panic in evidence serialization (#798)

* Add evidence variant conversions

Signed-off-by: Thane Thomson <connect@thanethomson.com>

* Add workaround to be able to keep Evidence serialization workaround

Signed-off-by: Thane Thomson <connect@thanethomson.com>

* Add test to reproduce original problem

Signed-off-by: Thane Thomson <connect@thanethomson.com>

* Update CHANGELOG

Signed-off-by: Thane Thomson <connect@thanethomson.com>

* Add delay to allow index to catch up

Signed-off-by: Thane Thomson <connect@thanethomson.com>

* Log raw RPC client responses at debug level

Signed-off-by: Thane Thomson <connect@thanethomson.com>

* Enable debug logging for kvstore-test

Signed-off-by: Thane Thomson <connect@thanethomson.com>

* Re-enable fail fast

Signed-off-by: Thane Thomson <connect@thanethomson.com>

* Add debug variant of test-all-features cargo command

Signed-off-by: Thane Thomson <connect@thanethomson.com>

* Enable debug logging for kvstore test

Signed-off-by: Thane Thomson <connect@thanethomson.com>

* Fix CI commands for kvstore tests

Signed-off-by: Thane Thomson <connect@thanethomson.com>

## Patch
### .github/workflows/test.yml
```diff
@@ -112,7 +112,9 @@ jobs:
       - uses: actions-rs/cargo@v1
         with:
           command: test-all-features
-          args: --manifest-path tools/kvstore-test/Cargo.toml
+          args: --manifest-path tools/kvstore-test/Cargo.toml -- --nocapture
+        env:
+          RUST_LOG: debug
 
   kvstore-integration-latest:
     runs-on: ubuntu-latest
```

### CHANGELOG.md
```diff
@@ -1,3 +1,12 @@
+## Unreleased
+
+### BUG FIXES
+
+* `[tendermint-proto]` Fix panic in evidence serialization in the case where we
+  receive an empty evidence Protobuf structure ([#782])
+
+[#782]: https://github.com/informalsystems/tendermint-rs/issues/782
+
 ## v0.18.0
 
 *Jan 29, 2021*
```

### proto/src/serializers/evidence.rs
```diff
@@ -8,6 +8,8 @@ use crate::tendermint::types::Evidence;
 #[derive(Clone, PartialEq, ::serde::Deserialize, ::serde::Serialize)]
 #[serde(tag = "type", content = "value")]
 pub enum EvidenceVariant {
+    /// Provided for when the evidence struct's optional `sum` field is `None`.
+    None,
     #[serde(rename = "tendermint/DuplicateVoteEvidence")]
     DuplicateVoteEvidence(crate::tendermint::types::DuplicateVoteEvidence),
     #[serde(rename = "tendermint/LightClientAttackEvidence")]
@@ -17,34 +19,56 @@ pub enum EvidenceVariant {
 impl From<EvidenceVariant> for Evidence {
     fn from(value: EvidenceVariant) -> Self {
         match value {
-            EvidenceVariant::DuplicateVoteEvidence(d) => Evidence {
-                sum: Some(Sum::DuplicateVoteEvidence(d)),
-            },
-            EvidenceVariant::LightClientAttackEvidence(l) => Evidence {
-                sum: Some(Sum::LightClientAttackEvidence(l)),
+            EvidenceVariant::None => Evidence { sum: None },
+            _ => Evidence {
+                sum: Some(value.into()),
             },
         }
     }
 }
 
 impl From<Evidence> for EvidenceVariant {
     fn from(value: Evidence) -> Self {
-        let sum = value.sum.unwrap(); // Todo: Error handling
-        match sum {
-            Sum::DuplicateVoteEvidence(d) => Self::DuplicateVoteEvidence(d),
-            Sum::LightClientAttackEvidence(l) => Self::LightClientAttackEvidence(l),
+        match value.sum {
+            Some(sum) => sum.into(),
+            None => Self::None,
         }
     }
 }
 
 impl From<Sum> for EvidenceVariant {
-    fn from(_: Sum) -> Self {
-        unimplemented!() // Prost adds extra annotations on top of Sum that are not used.
+    fn from(value: Sum) -> Self {
+        match value {
+            Sum::DuplicateVoteEvidence(d) => Self::DuplicateVoteEvidence(d),
+            Sum::LightClientAttackEvidence(l) => Self::LightClientAttackEvidence(l),
+        }
     }
 }
 
 impl From<EvidenceVariant> for Sum {
-    fn from(_: EvidenceVariant) -> Self {
-        unimplemented!() // Prost adds extra annotations on top of Sum that are not used.
+    fn from(value: EvidenceVariant) -> Self {
+        match value {
+            // This should never be called - should be handled instead in the
+            // `impl From<EvidenceVariant> for Evidence` above.
+            EvidenceVariant::None => {
+                panic!("non-existent evidence cannot be converted into its protobuf representation")
+            }
+            EvidenceVariant::DuplicateVoteEvidence(d) => Self::DuplicateVoteEvidence(d),
+            EvidenceVariant::LightClientAttackEvidence(l) => Self::LightClientAttackEvidence(l),
+        }
+    }
+}
+
+#[cfg(test)]
+mod test {
+    use super::*;
+
+    // Minimally reproduce https://github.com/informalsystems/tendermint-rs/issues/782
+    #[test]
+    fn empty_evidence() {
+        let ev = Evidence { sum: None };
+        let ev_json = serde_json::to_string(&ev).unwrap();
+        let ev_deserialized = serde_json::from_str::<Evidence>(&ev_json).unwrap();
+        assert_eq!(ev, ev_deserialized);
     }
 }
```

### rpc/src/client/transport/http.rs
```diff
@@ -7,7 +7,8 @@ use hyper::header;
 use tendermint::net;
 
 use crate::client::transport::utils::get_tcp_host_port;
-use crate::{Client, Response, Result, SimpleRequest};
+use crate::{Client, Error, Response, Result, SimpleRequest};
+use std::io::Read;
 
 /// A JSON-RPC/HTTP Tendermint RPC client (implements [`Client`]).
 ///
@@ -67,8 +68,14 @@ impl Client for HttpClient {
 
         let http_client = hyper::Client::new();
         let response = http_client.request(request).await?;
-        let response_body = hyper::body::aggregate(response.into_body()).await?;
-        R::Response::from_reader(response_body.reader())
+        let mut response_body = String::new();
+        hyper::body::aggregate(response.into_body())
+            .await?
+            .reader()
+            .read_to_string(&mut response_body)
+            .map_err(|_| Error::client_internal_error("failed to read response body to string"))?;
+        tracing::debug!("Incoming response: {}", response_body);
+        R::Response::from_string(&response_body)
     }
 }
 
```

### rpc/src/client/transport/websocket.rs
```diff
@@ -179,6 +179,7 @@ impl Client for WebSocketClient {
         let response = response_rx.recv().await.ok_or_else(|| {
             Error::client_internal_error("failed to hear back from WebSocket driver".to_string())
         })??;
+        tracing::debug!("Incoming response: {}", response);
         R::Response::from_string(response)
     }
 }
```

### tools/kvstore-test/Cargo.toml
```diff
@@ -14,4 +14,6 @@ tendermint = { version = "0.18.0", path = "../../tendermint" }
 tendermint-light-client = { version = "0.18.0", path = "../../light-client", features = ["unstable"] }
 tendermint-rpc = { version = "0.18.0", path = "../../rpc", features = [ "http-client", "websocket-client" ] }
 tokio = { version = "1.0", features = [ "rt-multi-thread", "macros" ] }
+tracing = "0.1"
+tracing-subscriber = "0.2"
 contracts = "0.4.0"
```

### tools/kvstore-test/Makefile.toml
```diff
@@ -3,6 +3,7 @@ CONTAINER_NAME = "kvstore-test"
 DOCKER_IMAGE = "informaldev/tendermint:0.34.0"
 HOST_RPC_PORT = 26657
 CARGO_MAKE_WAIT_MILLISECONDS = 1000
+RUST_LOG = "debug"
 
 [tasks.default]
 clear = true
@@ -17,7 +18,7 @@ args = ["run", "--name", "${CONTAINER_NAME}", "--rm", "--publish", "26657:${HOST
 dependencies = ["docker-up-stop-old", "docker-up-rm-old"]
 
 [tasks.test]
-args = ["test-all-features"]
+args = ["test", "--all-features", "--", "--nocapture"]
 
 [tasks.docker-stop]
 command = "docker"
```

### tools/kvstore-test/tests/tendermint.rs
```diff
@@ -17,10 +17,13 @@
 mod rpc {
     use std::cmp::min;
 
-    use tendermint_rpc::{Client, HttpClient, Id, Order, SubscriptionClient, WebSocketClient};
+    use tendermint_rpc::{
+        Client, HttpClient, Id, Order, SubscriptionClient, WebSocketClient, WebSocketClientDriver,
+    };
 
     use futures::StreamExt;
     use std::convert::TryFrom;
+    use std::sync::atomic::{AtomicU8, Ordering};
     use tendermint::abci::Log;
     use tendermint::abci::{Code, Transaction};
     use tendermint::block::Height;
@@ -30,22 +33,40 @@ mod rpc {
     use tendermint_rpc::query::{EventType, Query};
     use tokio::time::Duration;
 
-    pub fn localhost_rpc_client() -> HttpClient {
+    static LOGGING_INIT: AtomicU8 = AtomicU8::new(0);
+
+    fn init_logging() {
+        // Try to only initialize the logging once
+        if LOGGING_INIT.fetch_add(1, Ordering::SeqCst) == 0 {
+            tracing_subscriber::fmt::init();
+            tracing::info!("Test logging initialized");
+        }
+    }
+
+    pub fn localhost_http_client() -> HttpClient {
+        init_logging();
         HttpClient::new("tcp://127.0.0.1:26657".parse().unwrap()).unwrap()
     }
 
+    pub async fn localhost_websocket_client() -> (WebSocketClient, WebSocketClientDriver) {
+        init_logging();
+        WebSocketClient::new("tcp://127.0.0.1:26657".parse().unwrap())
+            .await
+            .unwrap()
+    }
+
     /// `/health` endpoint
     #[tokio::test]
     async fn health() {
-        let result = localhost_rpc_client().health().await;
+        let result = localhost_http_client().health().await;
 
         assert!(result.is_ok(), "health check failed");
     }
 
     /// `/abci_info` endpoint
     #[tokio::test]
     async fn abci_info() {
-        let abci_info = localhost_rpc_client().abci_info().await.unwrap();
+        let abci_info = localhost_http_client().abci_info().await.unwrap();
 
         assert_eq!(abci_info.app_version, 1u64);
         assert_eq!(abci_info.data.is_empty(), false);
@@ -55,7 +76,7 @@ mod rpc {
     #[tokio::test]
     async fn abci_query() {
         let key = "unpopulated_key".parse().unwrap();
-        let abci_query = localhost_rpc_client()
+        let abci_query = localhost_http_client()
             .abci_query(Some(key), vec![], None, false)
             .await
             .unwrap();
@@ -76,7 +97,7 @@ mod rpc {
     #[tokio::test]
     async fn block() {
         let height = 1u64;
-        let block_info = localhost_rpc_client()
+        let block_info = localhost_http_client()
             .block(Height::try_from(height).unwrap())
             .await
             .unwrap();
@@ -109,7 +130,7 @@ mod rpc {
     #[tokio::test]
     async fn block_results() {
         let height = 1u64;
-        let block_results = localhost_rpc_client()
+        let block_results = localhost_http_client()
             .block_results(Height::try_from(height).unwrap())
             .await
             .unwrap();
@@ -122,7 +143,7 @@ mod rpc {
     #[tokio::test]
     async fn blockchain() {
         let max_height = 10u64;
-        let blockchain_info = localhost_rpc_client()
+        let blockchain_info = localhost_http_client()
             .blockchain(Height::from(1u32), Height::try_from(max_height).unwrap())
             .await
             .unwrap();
@@ -137,7 +158,7 @@ mod rpc {
     #[tokio::test]
     async fn commit() {
         let height = 1u64;
-        let commit_info = localhost_rpc_client()
+        let commit_info = localhost_http_client()
             .commit(Height::try_from(height).unwrap())
             .await
             .unwrap();
@@ -154,13 +175,13 @@ mod rpc {
     #[tokio::test]
     async fn consensus_state() {
         // TODO(thane): Test more than just the deserialization.
-        localhost_rpc_client().consensus_state().await.unwrap();
+        localhost_http_client().consensus_state().await.unwrap();
     }
 
     /// `/genesis` endpoint
     #[tokio::test]
     async fn genesis() {
-        let genesis = localhost_rpc_client().genesis().await.unwrap(); // https://github.com/tendermint/tendermint/issues/5549
+        let genesis = localhost_http_client().genesis().await.unwrap(); // https://github.com/tendermint/tendermint/issues/5549
 
         assert_eq!(
             genesis.consensus_params.validator.pub_key_types[0].to_string(),
@@ -171,25 +192,23 @@ mod rpc {
     /// `/net_info` endpoint integration test
     #[tokio::test]
     async fn net_info() {
-        let net_info = localhost_rpc_client().net_info().await.unwrap();
+        let net_info = localhost_http_client().net_info().await.unwrap();
 
         assert!(net_info.listening);
     }
 
     /// `/status` endpoint integration test
     #[tokio::test]
     async fn status_integration() {
-        let status = localhost_rpc_client().status().await.unwrap();
+        let status = localhost_http_client().status().await.unwrap();
 
         // For lack of better things to test
         assert_eq!(status.validator_info.voting_power.value(), 10);
     }
 
     #[tokio::test]
     async fn subscription_interface() {
-        let (client, driver) = WebSocketClient::new("tcp://127.0.0.1:26657".parse().unwrap())
-            .await
-            .unwrap();
+        let (client, driver) = localhost_websocket_client().await;
         let driver_handle = tokio::spawn(async move { driver.run().await });
         let mut subs = client.subscribe(EventType::NewBlock.into()).await.unwrap();
         let mut ev_count = 5_i32;
@@ -220,9 +239,7 @@ mod rpc {
     }
 
     async fn simple_transaction_subscription() {
-        let (client, driver) = WebSocketClient::new("tcp://127.0.0.1:26657".parse().unwrap())
-            .await
-            .unwrap();
+        let (client, driver) = localhost_websocket_client().await;
         let driver_handle = tokio::spawn(async move { driver.run().await });
         let mut subs = client.subscribe(EventType::Tx.into()).await.unwrap();
         // We use Id::uuid_v4() here as a quick hack to generate a random value.
@@ -289,9 +306,7 @@ mod rpc {
     }
 
     async fn concurrent_subscriptions() {
-        let (client, driver) = WebSocketClient::new("tcp://127.0.0.1:26657".parse().unwrap())
-            .await
-            .unwrap();
+        let (client, driver) = localhost_websocket_client().await;
         let driver_handle = tokio::spawn(async move { driver.run().await });
         let new_block_subs = client.subscribe(EventType::NewBlock.into()).await.unwrap();
         let tx_subs = client.subscribe(EventType::Tx.into()).await.unwrap();
@@ -352,11 +367,8 @@ mod rpc {
     }
 
     async fn tx_search() {
-        let rpc_client = localhost_rpc_client();
-        let (mut subs_client, driver) =
-            WebSocketClient::new("tcp://127.0.0.1:26657".parse().unwrap())
-                .await
-                .unwrap();
+        let rpc_client = localhost_http_client();
+        let (mut subs_client, driver) = localhost_websocket_client().await;
         let driver_handle = tokio::spawn(async move { driver.run().await });
 
         let tx = "tx_search_key=tx_search_value".to_string();
@@ -369,6 +381,10 @@ mod rpc {
         .unwrap();
         println!("Got tx_info: {:?}", tx_info);
 
+        // TODO(thane): Find a better way of accomplishing this. This might
+        //              still be nondeterministic.
+        tokio::time::sleep(Duration::from_millis(500)).await;
+
         let res = rpc_client
             .tx_search(
                 Query::eq("app.key", "tx_search_key"),
```
