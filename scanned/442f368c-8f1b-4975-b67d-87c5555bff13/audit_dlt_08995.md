# [?] [fix] #1716: Fix consensus failure with f=0 cases (#2124)

## Summary
Severity: Unknown
Chain: Hyperledger Iroha
Component: hyperledger-iroha/iroha
Published: 2022-04-22
Source: https://github.com/hyperledger-iroha/iroha/commit/aae24c3114f99404c403e0ecf26c1ca5b58acbd0
Type: security-commit

## Details
[fix] #1716: Fix consensus failure with f=0 cases (#2124)

## Patch
### Cargo.lock
```diff
@@ -476,16 +476,16 @@ dependencies = [
 
 [[package]]
 name = "clap"
-version = "3.1.8"
+version = "3.1.10"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "71c47df61d9e16dc010b55dba1952a57d8c215dbb533fd13cdd13369aac73b1c"
+checksum = "3124f3f75ce09e22d1410043e1e24f2ecc44fad3afe4f08408f1f7663d68da2b"
 dependencies = [
  "atty",
  "bitflags",
  "clap_derive",
+ "clap_lex",
  "indexmap",
  "lazy_static",
- "os_str_bytes",
  "strsim 0.10.0",
  "termcolor",
  "textwrap 0.15.0",
@@ -504,6 +504,15 @@ dependencies = [
  "syn",
 ]
 
+[[package]]
+name = "clap_lex"
+version = "0.1.1"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "189ddd3b5d32a70b35e7686054371742a937b0d99128e76dde6340210e966669"
+dependencies = [
+ "os_str_bytes",
+]
+
 [[package]]
 name = "color-eyre"
 version = "0.5.11"
@@ -2174,7 +2183,7 @@ checksum = "67c21572b4949434e4fc1e1978b99c5f77064153c59d998bf13ecd96fb5ecba7"
 name = "kura_inspector"
 version = "2.0.0-pre-rc.3"
 dependencies = [
- "clap 3.1.8",
+ "clap 3.1.10",
  "futures-util",
  "iroha_config",
  "iroha_core",
@@ -2515,9 +2524,6 @@ name = "os_str_bytes"
 version = "6.0.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "8e22443d1643a904602595ba1cd8f7d896afe56d26712531c5ff73a15b2fbf64"
-dependencies = [
- "memchr",
-]
 
 [[package]]
 name = "owo-colors"
@@ -2555,7 +2561,7 @@ dependencies = [
 name = "parity_scale_decoder"
 version = "2.0.0-pre-rc.3"
 dependencies = [
- "clap 3.1.8",
+ "clap 3.1.10",
  "colored",
  "eyre",
  "iroha_core",
```

### client/tests/integration/connected_peers.rs
```diff
@@ -14,13 +14,6 @@ fn connected_peers_with_f_2_1_2() {
 }
 
 #[test]
-// TODO This case does not have to be supported, but at least have to
-// be error-handled AP: Re-opening
-// [#1716](https://github.com/hyperledger/iroha/issues/1716). The
-// solution might be to add a field to status that indicates whether
-// or not there have been many view changes.
-#[ignore]
-#[should_panic] // Stop gap solution until we fix 1716.
 fn connected_peers_with_f_1_0_1() {
     connected_peers_with_f(1)
 }
```

### client/tests/integration/unstable_network.rs
```diff
@@ -64,7 +64,6 @@ fn unstable_network(
     let (network, mut iroha_client) = rt.block_on(async {
         let mut configuration = Configuration::test();
         configuration.queue.maximum_transactions_in_block = MAXIMUM_TRANSACTIONS_IN_BLOCK;
-        configuration.sumeragi.n_topology_shifts_before_reshuffle = u64::from(n_peers);
         configuration.logger.max_log_level = Level(logger::Level::ERROR).into();
         let network =
             <Network>::new_with_offline_peers(Some(configuration), n_peers, n_offline_peers)
```

### config/src/lib.rs
```diff
@@ -157,7 +157,7 @@ pub mod logger {
     }
 }
 
-/// Trait for dynamic and asynchronous configuration via maintanence endpoint for rust structures
+/// Trait for dynamic and asynchronous configuration via maintenance endpoint for rust structures
 pub trait Configurable: Serialize + DeserializeOwned {
     /// Error type returned by methods of trait
     type Error;
```

### core/src/block.rs
```diff
@@ -719,7 +719,7 @@ impl VersionedCommittedBlock {
 }
 
 /// When Kura receives `ValidBlock`, the block is stored and
-/// then sent to later stage of the pipeline as `CommitedBlock`.
+/// then sent to later stage of the pipeline as `CommittedBlock`.
 #[version_with_scale(n = 1, versioned = "VersionedCommittedBlock")]
 #[derive(Debug, Clone, Decode, Encode, IntoSchema)]
 pub struct CommittedBlock {
```

### core/src/genesis.rs
```diff
@@ -134,7 +134,6 @@ async fn try_get_online_topology(
             .with_leader(this_peer_id.clone())
             .with_set_a(set_a)
             .with_set_b(set_b)
-            .reshuffle_after(network_topology.reshuffle_after())
             .build()
             .expect("Preconditions should be already checked.")
     };
```

### core/src/sumeragi/config.rs
```diff
@@ -14,7 +14,6 @@ pub const DEFAULT_BLOCK_TIME_MS: u64 = 1000;
 pub const DEFAULT_COMMIT_TIME_MS: u64 = 2000;
 /// Default amount of time Peer waits for `TxReceipt` from the leader.
 pub const DEFAULT_TX_RECEIPT_TIME_MS: u64 = 500;
-const DEFAULT_N_TOPOLOGY_SHIFTS_BEFORE_RESHUFFLE: u64 = 1;
 const DEFAULT_MAILBOX_SIZE: u32 = 100;
 const DEFAULT_GOSSIP_PERIOD_MS: u64 = 1000;
 const DEFAULT_GOSSIP_BATCH_SIZE: u32 = 500;
@@ -39,8 +38,6 @@ pub struct SumeragiConfiguration {
     pub commit_time_ms: u64,
     /// Amount of time Peer waits for TxReceipt from the leader.
     pub tx_receipt_time_ms: u64,
-    /// After N view changes topology will change tactic from shifting by one, to reshuffle.
-    pub n_topology_shifts_before_reshuffle: u64,
     /// Limits to which transactions must adhere
     pub transaction_limits: TransactionLimits,
     /// Mailbox size
@@ -60,7 +57,6 @@ impl Default for SumeragiConfiguration {
             block_time_ms: DEFAULT_BLOCK_TIME_MS,
             commit_time_ms: DEFAULT_COMMIT_TIME_MS,
             tx_receipt_time_ms: DEFAULT_TX_RECEIPT_TIME_MS,
-            n_topology_shifts_before_reshuffle: DEFAULT_N_TOPOLOGY_SHIFTS_BEFORE_RESHUFFLE,
             transaction_limits: TransactionLimits {
                 max_instruction_number: transaction::DEFAULT_MAX_INSTRUCTION_NUMBER,
                 max_wasm_size_bytes: transaction::DEFAULT_MAX_WASM_SIZE_BYTES,
```

### core/src/sumeragi/fault.rs
```diff
@@ -121,7 +121,6 @@ impl<G: GenesisNetworkTrait, K: KuraTrait<World = W>, W: WorldTrait, F: FaultInj
     ) -> Result<Self> {
         let network_topology = Topology::builder()
             .at_block(EmptyChainHash::default().into())
-            .reshuffle_after(configuration.n_topology_shifts_before_reshuffle)
             .with_peers(configuration.trusted_peers.peers.clone())
             .build()?;
 
@@ -678,6 +677,15 @@ impl<G: GenesisNetworkTrait, K: KuraTrait, W: WorldTrait, F: FaultInjection>
         }
         let signed_block = block.sign(self.key_pair.clone())?;
         if !network_topology.is_consensus_required() {
+            self.broadcast_msg_to(
+                BlockCommitted::from(signed_block.clone()),
+                network_topology
+                    .validating_peers()
+                    .iter()
+                    .chain(std::iter::once(network_topology.leader()))
+                    .chain(network_topology.peers_set_b()),
+            )
+            .await;
             self.commit_block(signed_block).await;
             return Ok(());
         }
@@ -775,6 +783,10 @@ impl<G: GenesisNetworkTrait, K: KuraTrait, W: WorldTrait, F: FaultInjection>
             self.invalidated_blocks_hashes.push(hash)
         }
         self.topology.apply_view_change(proof.clone());
+        self.wsv
+            .metrics
+            .view_changes
+            .set(self.number_of_view_changes());
         self.voting_block = None;
         error!(
             peer_addr = %self.peer_id.address,
```

### core/src/sumeragi/network_topology.rs
```diff
@@ -70,8 +70,6 @@ pub struct GenesisBuilder {
     set_a: Option<HashSet<PeerId>>,
 
     set_b: Option<HashSet<PeerId>>,
-
-    reshuffle_after_n_view_changes: Option<u64>,
 }
 
 impl GenesisBuilder {
@@ -98,12 +96,6 @@ impl GenesisBuilder {
         self
     }
 
-    /// Set `reshuffle_after_n_view_changes` config param.
-    pub fn reshuffle_after(mut self, n_view_changes: u64) -> Self {
-        self.reshuffle_after_n_view_changes = Some(n_view_changes);
-        self
-    }
-
     /// Build and get topology.
     ///
     /// # Errors
@@ -114,8 +106,6 @@ impl GenesisBuilder {
         let leader = field_is_some_or_err!(self.leader)?;
         let mut set_a = field_is_some_or_err!(self.set_a)?;
         let mut set_b = field_is_some_or_err!(self.set_b)?;
-        let reshuffle_after_n_view_changes =
-            field_is_some_or_err!(self.reshuffle_after_n_view_changes)?;
         let max_faults_rem = (set_a.len() - 1) % 2;
         if max_faults_rem > 0 {
             return Err(eyre!("Could not deduce max faults. As given: 2f+1=set_a.len() We get a non integer f. f should be an integer."));
@@ -137,7 +127,6 @@ impl GenesisBuilder {
             .collect();
         Ok(Topology {
             sorted_peers,
-            reshuffle_after_n_view_changes,
             at_block: EmptyChainHash::default().into(),
             view_change_proofs: ViewChangeProofs::empty(),
         })
@@ -150,11 +139,9 @@ impl GenesisBuilder {
 pub struct Builder {
     /// Current order of peers. The roles of peers are defined based on this order.
     peers: Option<HashSet<PeerId>>,
-
-    reshuffle_after_n_view_changes: Option<u64>,
-
+    /// Hash of the last committed block.
     at_block: Option<HashOf<VersionedCommittedBlock>>,
-
+    /// [`ViewChangeProofs`] accumulated during this round.
     view_change_proofs: ViewChangeProofs,
 }
 
@@ -170,12 +157,6 @@ impl Builder {
         self
     }
 
-    /// Set `reshuffle_after_n_view_changes` config param.
-    pub fn reshuffle_after(mut self, n_view_changes: u64) -> Self {
-        self.reshuffle_after_n_view_changes = Some(n_view_changes);
-        self
-    }
-
     /// Set the latest committed block.
     pub fn at_block(mut self, block: HashOf<VersionedCommittedBlock>) -> Self {
         self.at_block = Some(block);
@@ -196,25 +177,22 @@ impl Builder {
     pub fn build(self) -> Result<Topology> {
         let peers = field_is_some_or_err!(self.peers)?;
         if peers.is_empty() {
-            return Err(eyre::eyre!(
-                "There must be at least one peer in the network."
-            ));
+            return Err(eyre!("There must be at least one peer in the network."));
         }
-        let reshuffle_after_n_view_changes =
-            field_is_some_or_err!(self.reshuffle_after_n_view_changes)?;
         let at_block = field_is_some_or_err!(self.at_block)?;
-
         let peers: Vec<_> = peers.into_iter().collect();
-        let sorted_peers = if self.view_change_proofs.len() as u64 > reshuffle_after_n_view_changes
-        {
-            sort_peers_by_hash_and_counter(peers, &at_block, self.view_change_proofs.len() as u64)
+        let n_view_changes = self.view_change_proofs.len();
+        let since_last_shuffle = n_view_changes % peers.len();
+        let is_full_circle = since_last_shuffle == 0;
+        let sorted_peers = if is_full_circle {
+            sort_peers_by_hash_and_counter(peers, &at_block, n_view_changes as u64)
         } else {
-            let peers = sort_peers_by_hash(peers, &at_block);
-            shift_peers_by_n(peers, self.view_change_proofs.len() as u64)
+            let last_shuffled_at = n_view_changes - since_last_shuffle;
+            let peers = sort_peers_by_hash_and_counter(peers, &at_block, last_shuffled_at as u64);
+            shift_peers_by_n(peers, since_last_shuffle as u64)
         };
         Ok(Topology {
             sorted_peers,
-            reshuffle_after_n_view_changes,
             at_block,
             view_change_proofs: self.view_change_proofs,
         })
@@ -226,11 +204,9 @@ impl Builder {
 pub struct Topology {
     /// Current order of peers. The roles of peers are defined based on this order.
     sorted_peers: Vec<PeerId>,
-
-    reshuffle_after_n_view_changes: u64,
-
+    /// Hash of the last committed block.
     at_block: HashOf<VersionedCommittedBlock>,
-
+    /// [`ViewChangeProofs`] accumulated during this round.
     view_change_proofs: ViewChangeProofs,
 }
 
@@ -244,7 +220,6 @@ impl Topology {
     pub fn into_builder(self) -> Builder {
         Builder {
             peers: Some(self.sorted_peers.into_iter().collect()),
-            reshuffle_after_n_view_changes: Some(self.reshuffle_after_n_view_changes),
             at_block: Some(self.at_block),
             view_change_proofs: self.view_change_proofs,
         }
@@ -277,7 +252,7 @@ impl Topology {
 
     /// Answers if the consensus stage is required with the current number of peers.
     pub fn is_consensus_required(&self) -> bool {
-        self.sorted_peers.len() > 1
+        self.min_votes_for_commit() > 1
     }
 
     /// The minimum number of signatures needed to commit a block
@@ -389,11 +364,6 @@ impl Topology {
         &self.sorted_peers[..]
     }
 
-    /// Config param telling topology when to reshuffle at view change.
-    pub const fn reshuffle_after(&self) -> u64 {
-        self.reshuffle_after_n_view_changes
-    }
-
     /// Block hash on which this topology is based.
     pub const fn at_block(&self) -> &HashOf<VersionedCommittedBlock> {
         &self.at_block
@@ -475,7 +445,6 @@ mod tests {
             .with_leader(peer_1)
             .with_set_a(set_a)
             .with_set_b(set_b)
-            .reshuffle_after(1)
             .build()
             .expect("Failed to create topology.");
     }
@@ -490,7 +459,6 @@ mod tests {
             .with_leader(peers.iter().next().unwrap().clone())
             .with_set_a(set_a)
             .with_set_b(set_b)
-            .reshuffle_after(1)
             .build()
             .expect("Failed to create topology.");
     }
@@ -571,4 +539,48 @@ mod tests {
         let peers_2 = sort_peers_by_hash_and_counter(peers, &hash, 2);
         assert_ne!(peers_1, peers_2);
     }
+
+    #[test]
+    fn topology_shifts_or_shuffles() -> Result<()> {
+        let peers = topology_test_peers();
+        let n_peers = peers.len();
+        let dummy_hash = Hash::prehashed([0_u8; Hash::LENGTH]).typed();
+        let dummy_proof = crate::sumeragi::Proof::commit_timeout(
+            dummy_hash,
+            dummy_hash.transmute(),
+            dummy_hash.transmute(),
+            KeyPair::generate()?,
+        )?;
+        let mut last_topology = Builder::new()
+            .with_peers(peers)
+            .at_block(dummy_hash.transmute())
+            .build()?;
+        for _a_view_change in 0..2 * n_peers {
+            let mut topology = last_topology.clone();
+            // When
+            last_topology.sorted_peers.rotate_right(1);
+            topology.apply_view_change(dummy_proof.clone());
+            // Then
+            let is_shifted_by_one = last_topology.sorted_peers == topology.sorted_peers;
+            let nth_view_change = topology.view_change_proofs.len();
+            let is_full_circle = nth_view_change % n_peers == 0;
+            if is_full_circle {
+                // `topology` should have shuffled
+                if is_shifted_by_one {
+                    return Err(eyre!(
+                        "At {nth_view_change}: shifted by one despite full circle"
+                    ));
+                }
+            } else {
+                // `topology` should have shifted by one
+                if !is_shifted_by_one {
+                    return Err(eyre!(
+                        "At {nth_view_change}: not shifted by one despite incomplete circle"
+                    ));
+                }
+            }
+            last_topology = topology;
+        }
+        Ok(())
+    }
 }
```

### core/test_network/src/lib.rs
```diff
@@ -232,11 +232,9 @@ where
         n_peers: u32,
         max_txs_in_block: u32,
         offline_peers: u32,
-        n_shifts: u64,
     ) -> (Self, Client) {
         let mut configuration = Configuration::test();
         configuration.queue.maximum_transactions_in_block = max_txs_in_block;
-        configuration.sumeragi.n_topology_shifts_before_reshuffle = n_shifts;
         let network = Network::new_with_offline_peers(Some(configuration), n_peers, offline_peers)
             .await
             .expect("Failed to init peers");
@@ -259,7 +257,6 @@ where
             n_peers,
             maximum_transactions_in_block,
             offline_peers,
-            SumeragiConfiguration::default().n_topology_shifts_before_reshuffle,
         )
         .await
     }
```

### docs/source/references/api_spec.md
```diff
@@ -227,14 +227,19 @@ Also returns current status of peer in json string:
   + Number of committed blocks (block height)
   + Total number of transactions
   + `uptime` since creation of the genesis block in milliseconds.
+  + Number of view_changes in the current round
 
 ```json
 {
     "peers": 3,
     "blocks": 1,
     "txs_accepted": 3,
     "txs_rejected": 0,
-    "uptime": 3200,
+    "uptime": {
+        "secs": 5,
+        "nanos": 937000000
+    },
+    "view_changes": 0
 }
 ```
 
@@ -251,25 +256,49 @@ Also returns current status of peer in json string:
 **Expects**: -
 
 **Responses**:
-- 200 OK - currently mirrors status:
-  + Number of connected peers, except for the reporting peer itself
-  + Number of committed blocks (block height)
-  + Total number of transactions
-  + `uptime` since creation of the genesis block in milliseconds.
+- 200 OK - reports 8 of 10 metrics:
 
 ```bash
+# HELP accounts User accounts registered at this time
+# TYPE accounts gauge
+accounts{domain="genesis"} 1
+accounts{domain="wonderland"} 1
 # HELP block_height Current block height
 # TYPE block_height counter
-block_height 0
+block_height 1
 # HELP connected_peers Total number of currently connected peers
 # TYPE connected_peers gauge
 connected_peers 0
+# HELP domains Total number of domains
+# TYPE domains gauge
+domains 2
+# HELP tx_amount average amount involved in a transaction on this peer
+# TYPE tx_amount histogram
+tx_amount_bucket{le="0.005"} 0
+tx_amount_bucket{le="0.01"} 0
+tx_amount_bucket{le="0.025"} 0
+tx_amount_bucket{le="0.05"} 0
+tx_amount_bucket{le="0.1"} 0
+tx_amount_bucket{le="0.25"} 0
+tx_amount_bucket{le="0.5"} 0
+tx_amount_bucket{le="1"} 0
+tx_amount_bucket{le="2.5"} 0
+tx_amount_bucket{le="5"} 0
+tx_amount_bucket{le="10"} 0
+tx_amount_bucket{le="+Inf"} 2
+tx_amount_sum 26
+tx_amount_count 2
 # HELP txs Transactions committed
 # TYPE txs counter
-txs 0
-# HELP uptime_since_genesis_ms Uptime of the network, starting from creation of the genesis block
+txs{type="accepted"} 1
+txs{type="rejected"} 0
+txs{type="total"} 1
+# HELP uptime_since_genesis_ms Network up-time, from creation of the genesis block
 # TYPE uptime_since_genesis_ms gauge
-uptime_since_genesis_ms 0
+uptime_since_genesis_ms 54572974
+# HELP view_changes Number of view_changes in the current round
+# TYPE view_changes gauge
+view_changes 0
 ```
 
 ## Parity Scale Codec
```

### docs/source/references/config.md
```diff
@@ -34,7 +34,6 @@ The following is the default configuration used by Iroha.
     ],
     "COMMIT_TIME_MS": 2000,
     "TX_RECEIPT_TIME_MS": 500,
-    "N_TOPOLOGY_SHIFTS_BEFORE_RESHUFFLE": 1,
     "TRANSACTION_LIMITS": {
       "max_instruction_number": 4096,
       "max_wasm_size_bytes": 4194304
@@ -473,7 +472,6 @@ Has type `SumeragiConfiguration`. Can be configured via environment variable `IR
   "GOSSIP_BATCH_SIZE": 500,
   "GOSSIP_PERIOD_MS": 1000,
   "MAILBOX": 100,
-  "N_TOPOLOGY_SHIFTS_BEFORE_RESHUFFLE": 1,
   "PEER_ID": {
     "address": "127.0.0.1:1337",
     "public_key": "ed01201c61faf8fe94e253b93114240394f79a607b7fa55f9e5a41ebec74b88055768b"
@@ -558,16 +556,6 @@ Has type `u32`. Can be configured via environment variable `SUMERAGI_MAILBOX`
 100
 ```
 
-### `sumeragi.n_topology_shifts_before_reshuffle`
-
-After N view changes topology will change tactic from shifting by one, to reshuffle.
-
-Has type `u64`. Can be configured via environment variable `SUMERAGI_N_TOPOLOGY_SHIFTS_BEFORE_RESHUFFLE`
-
-```json
-1
-```
-
 ### `sumeragi.peer_id`
 
 Current Peer Identification.
```
