# [?] Queue panic failure fix.

## Summary
Severity: Unknown
Chain: Hyperledger Iroha
Component: hyperledger-iroha/iroha
Published: 2021-09-28
Source: https://github.com/hyperledger-iroha/iroha/commit/1947e758be08bb4ce30ca37ad220d8e72b481678
Type: security-commit

## Details
Queue panic failure fix.

Signed-off-by: Egor Ivkov <e.o.ivkov@gmail.com>

## Patch
### .github/workflows/iroha2-dev.yml
```diff
@@ -56,31 +56,31 @@ jobs:
           context: .
           push: true
           tags: iroha1/iroha:iroha2-dev
-          build-args:
-            - TARGET_DIR=release
-            - PROFILE=--release
+          build-args: |
+            TARGET_DIR=release
+            PROFILE=--release
 
       - name: Build and push Iroha client cli Docker image
         uses: docker/build-push-action@v2
         with:
           context: .
           push: true
           tags: iroha1/iroha:iroha2-client-cli-dev
-          build-args:
-            - TARGET_DIR=release
-            - PROFILE=--release
-            - BIN=iroha_client_cli
+          build-args: |
+            TARGET_DIR=release
+            PROFILE=--release
+            BIN=iroha_client_cli
 
       - name: Build and push Iroha Crypto CLI Docker image
         uses: docker/build-push-action@v2
         with:
           context: .
           push: true
           tags: iroha1/iroha:iroha2-crypto-cli-dev
-          build-args:
-            - TARGET_DIR=release
-            - PROFILE=--release
-            - BIN=iroha_crypto_cli
+          build-args: |
+            TARGET_DIR=release
+            PROFILE=--release
+            BIN=iroha_crypto_cli
 
   # Coverage is both in PR and in push pipelines so that:
   # 1. PR can get coverage report from bot.
```

### docker-compose-local.yml
```diff
@@ -0,0 +1,58 @@
+version: "3.3"
+services:
+  iroha:
+    build:
+      context: .
+    image: iroha:debug
+    environment:
+      TORII_P2P_ADDR: iroha:1337
+      TORII_API_URL: iroha:8080
+      IROHA_PUBLIC_KEY: "ed01207233bfc89dcbd68c19fde6ce6158225298ec1131b6a130d1aeb454c1ab5183c0"
+      IROHA_PRIVATE_KEY: '{"digest_function": "ed25519", "payload": "9ac47abf59b356e0bd7dcbbbb4dec080e302156a48ca907e47cb6aea1d32719e7233bfc89dcbd68c19fde6ce6158225298ec1131b6a130d1aeb454c1ab5183c0"}'
+      SUMERAGI_TRUSTED_PEERS: '[{"address":"iroha:1337", "public_key": "ed01207233bfc89dcbd68c19fde6ce6158225298ec1131b6a130d1aeb454c1ab5183c0"}, {"address":"iroha2:1338", "public_key": "ed0120cc25624d62896d3a0bfd8940f928dc2abf27cc57cefeb442aa96d9081aae58a1"}, {"address": "iroha3:1339", "public_key": "ed0120faca9e8aa83225cb4d16d67f27dd4f93fc30ffa11adc1f5c88fd5495ecc91020"}, {"address": "iroha4:1340", "public_key": "ed01208e351a70b6a603ed285d666b8d689b680865913ba03ce29fb7d13a166c4e7f1f"}]'
+    ports:
+      - "1337:1337"
+      - "8080:8080"
+    command: ./iroha_cli --submit-genesis
+
+  iroha2:
+    depends_on:
+      - iroha
+    image: iroha:debug
+    environment:
+      TORII_P2P_ADDR: iroha2:1338
+      TORII_API_URL: iroha2:8081
+      IROHA_PUBLIC_KEY: "ed0120cc25624d62896d3a0bfd8940f928dc2abf27cc57cefeb442aa96d9081aae58a1"
+      IROHA_PRIVATE_KEY: '{"digest_function": "ed25519", "payload": "3bac34cda9e3763fa069c1198312d1ec73b53023b8180c822ac355435edc4a24cc25624d62896d3a0bfd8940f928dc2abf27cc57cefeb442aa96d9081aae58a1"}'
+      SUMERAGI_TRUSTED_PEERS: '[{"address":"iroha:1337", "public_key": "ed01207233bfc89dcbd68c19fde6ce6158225298ec1131b6a130d1aeb454c1ab5183c0"}, {"address":"iroha2:1338", "public_key": "ed0120cc25624d62896d3a0bfd8940f928dc2abf27cc57cefeb442aa96d9081aae58a1"}, {"address": "iroha3:1339", "public_key": "ed0120faca9e8aa83225cb4d16d67f27dd4f93fc30ffa11adc1f5c88fd5495ecc91020"}, {"address": "iroha4:1340", "public_key": "ed01208e351a70b6a603ed285d666b8d689b680865913ba03ce29fb7d13a166c4e7f1f"}]'
+    ports:
+      - "1338:1338"
+      - "8081:8081"
+
+  iroha3:
+    depends_on:
+      - iroha
+    image: iroha:debug
+    environment:
+      TORII_P2P_ADDR: iroha3:1339
+      TORII_API_URL: iroha3:8082
+      IROHA_PUBLIC_KEY: "ed0120faca9e8aa83225cb4d16d67f27dd4f93fc30ffa11adc1f5c88fd5495ecc91020"
+      IROHA_PRIVATE_KEY: '{"digest_function": "ed25519", "payload": "1261a436d36779223d7d6cf20e8b644510e488e6a50bafd77a7485264d27197dfaca9e8aa83225cb4d16d67f27dd4f93fc30ffa11adc1f5c88fd5495ecc91020"}'
+      SUMERAGI_TRUSTED_PEERS: '[{"address":"iroha:1337", "public_key": "ed01207233bfc89dcbd68c19fde6ce6158225298ec1131b6a130d1aeb454c1ab5183c0"}, {"address":"iroha2:1338", "public_key": "ed0120cc25624d62896d3a0bfd8940f928dc2abf27cc57cefeb442aa96d9081aae58a1"}, {"address": "iroha3:1339", "public_key": "ed0120faca9e8aa83225cb4d16d67f27dd4f93fc30ffa11adc1f5c88fd5495ecc91020"}, {"address": "iroha4:1340", "public_key": "ed01208e351a70b6a603ed285d666b8d689b680865913ba03ce29fb7d13a166c4e7f1f"}]'
+    ports:
+      - "1339:1339"
+      - "8082:8082"
+
+  iroha4:
+    depends_on:
+      - iroha
+    image: iroha:debug
+    environment:
+      TORII_P2P_ADDR: iroha4:1340
+      TORII_API_URL: iroha4:8083
+      IROHA_PUBLIC_KEY: "ed01208e351a70b6a603ed285d666b8d689b680865913ba03ce29fb7d13a166c4e7f1f"
+      IROHA_PRIVATE_KEY: '{"digest_function": "ed25519", "payload": "a70dab95c7482eb9f159111b65947e482108cfe67df877bd8d3b9441a781c7c98e351a70b6a603ed285d666b8d689b680865913ba03ce29fb7d13a166c4e7f1f"}'
+      SUMERAGI_TRUSTED_PEERS: '[{"address":"iroha:1337", "public_key": "ed01207233bfc89dcbd68c19fde6ce6158225298ec1131b6a130d1aeb454c1ab5183c0"}, {"address":"iroha2:1338", "public_key": "ed0120cc25624d62896d3a0bfd8940f928dc2abf27cc57cefeb442aa96d9081aae58a1"}, {"address": "iroha3:1339", "public_key": "ed0120faca9e8aa83225cb4d16d67f27dd4f93fc30ffa11adc1f5c88fd5495ecc91020"}, {"address": "iroha4:1340", "public_key": "ed01208e351a70b6a603ed285d666b8d689b680865913ba03ce29fb7d13a166c4e7f1f"}]'
+    ports:
+      - "1340:1340"
+      - "8083:8083"
```

### iroha/src/queue.rs
```diff
@@ -5,7 +5,6 @@ use std::time::Duration;
 use crossbeam_queue::ArrayQueue;
 use dashmap::{mapref::entry::Entry, DashMap};
 use eyre::Result;
-use iroha_data_model::prelude::*;
 
 use self::config::QueueConfiguration;
 use crate::{prelude::*, wsv::WorldTrait};
@@ -39,8 +38,8 @@ impl Queue {
     }
 
     /// Returns all pending transactions.
-    pub fn all_transactions(&'_ self) -> Vec<VersionedAcceptedTransaction> {
-        self.txs.iter().map(|e| e.value().clone()).collect()
+    pub fn all_transactions(&self) -> Vec<VersionedAcceptedTransaction> {
+        self.txs.iter().map(|t| t.value().clone()).collect()
     }
 
     /// Pushes transaction into queue
@@ -96,7 +95,11 @@ impl Queue {
     /// Pops single transaction.
     ///
     /// Records unsigned transaction in seen.
-    #[allow(clippy::expect_used, clippy::unwrap_in_result)]
+    #[allow(
+        clippy::expect_used,
+        clippy::unwrap_in_result,
+        clippy::cognitive_complexity
+    )]
     fn pop<W: WorldTrait>(
         &self,
         wsv: &WorldStateView<W>,
@@ -106,7 +109,8 @@ impl Queue {
             let hash = self.queue.pop()?;
             let entry = match self.txs.entry(hash) {
                 Entry::Occupied(entry) => entry,
-                Entry::Vacant(_) => unreachable!(),
+                // As practice shows this code is not `unreachable!()`. When transactions are submitted quickly it can be reached.
+                Entry::Vacant(_) => continue,
             };
 
             if entry.get().is_expired(self.ttl) {
@@ -115,14 +119,15 @@ impl Queue {
                 continue;
             }
             if entry.get().is_in_blockchain(wsv) {
+                iroha_logger::warn!("Transaction is already committed or rejected.");
                 entry.remove_entry();
                 continue;
             }
 
             let sig_condition = match entry.get().check_signature_condition(wsv) {
                 Ok(condition) => condition,
                 Err(error) => {
-                    iroha_logger::error!(%error, "Not passed signature condition");
+                    iroha_logger::error!(%error, "Error in signature condition validation");
                     entry.remove_entry();
                     continue;
                 }
@@ -206,7 +211,7 @@ mod tests {
         time::Duration,
     };
 
-    use iroha_data_model::{domain::DomainsMap, peer::PeersIds};
+    use iroha_data_model::{domain::DomainsMap, peer::PeersIds, prelude::*};
 
     use super::*;
     use crate::wsv::World;
@@ -474,12 +479,12 @@ mod tests {
         });
 
         let a = queue
-            .pop_avaliable(true, &wsv)
+            .get_transactions_for_block(&wsv)
             .into_iter()
             .map(|tx| tx.hash())
             .collect::<Vec<_>>();
         let b = queue
-            .pop_avaliable(true, &wsv)
+            .get_transactions_for_block(&wsv)
             .into_iter()
             .map(|tx| tx.hash())
             .collect::<Vec<_>>();
```

### iroha/src/sumeragi/mod.rs
```diff
@@ -216,8 +216,9 @@ impl<G: GenesisNetworkTrait, W: WorldTrait> SumeragiTrait for Sumeragi<G, W> {
 
 /// The interval at which sumeragi checks if there are tx in the `queue`.
 /// And will create a block if is leader and the voting is not already in progress.
-pub const TX_RETRIEVAL_INTERVAL: Duration = Duration::from_millis(100);
-pub const TX_GOSSIP_INTERVAL: Duration = Duration::from_millis(200);
+pub const TX_RETRIEVAL_INTERVAL: Duration = Duration::from_millis(200);
+/// The interval at which sumeragi forwards txs from `queue` to other peers.
+pub const TX_GOSSIP_INTERVAL: Duration = Duration::from_millis(100);
 /// The interval of peers (re)connection.
 pub const PEERS_CONNECT_INTERVAL: Duration = Duration::from_secs(1);
 
@@ -568,15 +569,14 @@ impl<G: GenesisNetworkTrait, W: WorldTrait> Sumeragi<G, W> {
             self.topology.role(&self.peer_id),
             transactions.len(),
         );
-        let leader = self.topology.leader().clone();
         let this_peer = self.peer_id.clone();
         let peers = self.topology.sorted_peers().to_vec();
         let transactions = transactions.to_vec();
         let mut send_futures = Vec::new();
         // TODO: send transactions in batch not to crowd message channels.
         for peer in &peers {
             for transaction in &transactions {
-                if peer != &leader && peer != &this_peer {
+                if peer != &this_peer {
                     let message = VersionedMessage::from(Message::from(TransactionForwarded::new(
                         transaction,
                         &this_peer,
```

### iroha/src/torii/mod.rs
```diff
@@ -70,9 +70,10 @@ pub enum Error {
     /// Error while getting or setting configuration
     #[error("Configuration error")]
     Config(#[source] ConfigError),
-    /// Queue is full
-    #[error("Queue is full")]
-    FullQueue,
+    //TODO: Have specific errors for each case in queue push failure
+    /// Failed to push into queue.
+    #[error("Failed to push into queue")]
+    PushIntoQueue,
 }
 
 impl Reply for Error {
@@ -84,7 +85,7 @@ impl Reply for Error {
                 ExecuteQuery(_)
                 | RequestPendingTransactions(_)
                 | DecodeRequestPendingTransactions(_)
-                | FullQueue
+                | PushIntoQueue
                 | EncodePendingTransactions(_) => StatusCode::INTERNAL_SERVER_ERROR,
                 TxTooBig | VersionedTransaction(_) | AcceptTransaction(_) | ValidateQuery(_) => {
                     StatusCode::BAD_REQUEST
@@ -242,7 +243,7 @@ async fn handle_instructions<W: WorldTrait>(
     state
         .queue
         .push(transaction, &*state.wsv)
-        .map_err(|_| Error::FullQueue)
+        .map_err(|_| Error::PushIntoQueue)
         .map(|()| Empty)
 }
 
```

### iroha/test_network/tests/sumeragi_with_mock.rs
```diff
@@ -314,6 +314,7 @@ pub mod utils {
                 self.broker.subscribe::<CommitBlock, _>(ctx);
                 self.broker.subscribe::<NetworkMessage, _>(ctx);
                 self.broker.subscribe::<Voting, _>(ctx);
+                self.broker.subscribe::<Gossip, _>(ctx);
                 ctx.notify_every::<ConnectPeers>(PEERS_CONNECT_INTERVAL);
             }
         }
@@ -394,6 +395,7 @@ pub mod utils {
                      + Handler<Voting, Result = ()>
                      + Handler<ConnectPeers, Result = ()>
                      + Handler<NetworkMessage, Result = ()>
+                     + Handler<Gossip, Result = ()>
         );
 
         #[derive(Debug, Clone, Copy, Default, Message)]
@@ -567,7 +569,7 @@ async fn blocks_applied(channels: &mut [mpsc::Receiver<Stored>], n: usize) {
     assert_eq!(out, vec![n; channels.len()]);
 }
 
-async fn send_tx<W, G, S, K, B>(network: &Network<W, G, S, K, B>, to_leader: bool)
+async fn start_round_with_tx<W, G, S, K, B>(network: &Network<W, G, S, K, B>, to_leader: bool)
 where
     W: WorldTrait,
     G: GenesisNetworkTrait,
@@ -590,6 +592,29 @@ where
         .await;
 }
 
+async fn put_tx_in_queue<W, G, S, K, B>(network: &Network<W, G, S, K, B>, to_leader: bool)
+where
+    W: WorldTrait,
+    G: GenesisNetworkTrait,
+    S: SumeragiTrait<GenesisNetwork = G, World = W> + Handler<sumeragi::Round>,
+    K: KuraTrait<World = W>,
+    B: BlockSynchronizerTrait<Sumeragi = S, World = W>,
+{
+    let tx = world::sign_tx(vec![]);
+    let leader = network.send(|iroha| &iroha.sumeragi, IsLeader).await;
+    let (_, peer) = leader
+        .into_iter()
+        .zip(network.peers())
+        .find(|(leader, _)| if to_leader { *leader } else { !*leader })
+        .unwrap();
+    peer.iroha
+        .as_ref()
+        .unwrap()
+        .queue
+        .push(tx, &*peer.iroha.as_ref().unwrap().wsv)
+        .unwrap();
+}
+
 #[tokio::test(flavor = "multi_thread")]
 #[ignore = "mock"]
 async fn all_peers_commit_block() {
@@ -609,7 +634,7 @@ async fn all_peers_commit_block() {
         .collect::<Vec<_>>();
 
     // Send tx to leader
-    send_tx(&network, true).await;
+    start_round_with_tx(&network, true).await;
     time::sleep(Duration::from_secs(2)).await;
 
     blocks_applied(&mut channels, 1).await;
@@ -634,7 +659,7 @@ async fn change_view_on_commit_timeout() {
         .collect::<Vec<_>>();
 
     // send to leader
-    send_tx(&network, true).await;
+    start_round_with_tx(&network, true).await;
     time::sleep(Duration::from_secs(2)).await;
 
     blocks_applied(&mut channels, 0).await;
@@ -673,7 +698,12 @@ async fn change_view_on_tx_receipt_timeout() {
         .collect::<Vec<_>>();
 
     // send to not leader
-    send_tx(&network, false).await;
+    put_tx_in_queue(&network, false).await;
+
+    // Let peers gossip tx.
+    for peer in network.peers() {
+        peer.iroha.as_ref().unwrap().sumeragi.do_send(Gossip).await;
+    }
 
     // Wait while tx is gossiped
     time::sleep(Duration::from_millis(500)).await;
@@ -714,7 +744,7 @@ async fn change_view_on_block_creation_timeout() {
         .collect::<Vec<_>>();
 
     // send to not leader
-    send_tx(&network, false).await;
+    start_round_with_tx(&network, false).await;
     time::sleep(Duration::from_secs(2)).await;
 
     blocks_applied(&mut channels, 0).await;
@@ -747,7 +777,7 @@ async fn not_enough_votes() {
         .collect::<Vec<_>>();
 
     // send to not leader
-    send_tx(&network, true).await;
+    start_round_with_tx(&network, true).await;
     time::sleep(Duration::from_secs(2)).await;
 
     blocks_applied(&mut channels, 0).await;
```

### iroha_client/tests/tests/multisignature_transaction.rs
```diff
@@ -12,7 +12,6 @@ use test_network::*;
 
 #[allow(clippy::too_many_lines)]
 #[test]
-#[ignore = "FIXME"]
 fn multisignature_transactions_should_wait_for_all_signatures() {
     let (_rt, network, _) = <Network>::start_test_with_runtime(4, 1);
     let pipeline_time = Configuration::pipeline_time();
@@ -77,7 +76,8 @@ fn multisignature_transactions_should_wait_for_all_signatures() {
     thread::sleep(pipeline_time);
 
     //Then
-    client_configuration.torii_api_url = network.peers.last().unwrap().api_address.clone();
+    client_configuration.torii_api_url =
+        "http://".to_owned() + &network.peers.last().unwrap().api_address;
     let mut iroha_client_1 = Client::new(&client_configuration);
     let request = client::asset::by_account_id(account_id);
     assert!(iroha_client_1
```
