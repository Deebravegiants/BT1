# [?] fix: prevent overflow in various calculations and add validation  (#5325)

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2026-09-21
Source: https://github.com/nervosnetwork/ckb/commit/4a44a5f1854eccc3f25e1e03671af20301824501
Type: security-commit

## Details
fix: prevent overflow in various calculations and add validation  (#5325)

### What problem does this PR solve?

Prevent overflow in numberic calculations and add validation for spec
parameters.

Problem Summary:

### What is changed and how it works?

Proposal: [xxx](url) <!-- REMOVE this line if not applicable -->

What's Changed:

### Related changes

- PR to update `owner/repo`:
- Need to cherry-pick to the release branch

### Check List <!--REMOVE the items that are not applicable-->

Tests <!-- At least one of them must be included. -->

- Unit test
- Integration test
- Manual test (add detailed scripts or steps below)
- No code

Side effects

- Performance regression
- Breaking backward compatibility

## Patch
### chain/src/utils/orphan_block_pool.rs
```diff
@@ -115,7 +115,7 @@ impl InnerPool {
             .get(parent_hash)
             .and_then(|map| {
                 map.iter().next().map(|(_, lonely_block)| {
-                    lonely_block.epoch_number() + EXPIRED_EPOCH < tip_epoch
+                    tip_epoch.saturating_sub(lonely_block.epoch_number()) > EXPIRED_EPOCH
                 })
             })
             .unwrap_or_default()
```

### spec/src/error.rs
```diff
@@ -20,6 +20,10 @@ pub enum SpecError {
         /// The actual calculated hash
         actual: Byte32,
     },
+
+    /// The chain specification contains invalid consensus parameters.
+    #[error("InvalidParams: {0}")]
+    InvalidParams(String),
 }
 
 impl From<SpecError> for Error {
```

### spec/src/lib.rs
```diff
@@ -15,7 +15,7 @@ use crate::consensus::{
     TESTNET_ACTIVATION_THRESHOLD, TYPE_ID_CODE_HASH, build_genesis_dao_data,
     build_genesis_epoch_ext,
 };
-use crate::versionbits::{ActiveMode, Deployment, DeploymentPos};
+use crate::versionbits::{ActiveMode, Deployment, DeploymentPos, VERSIONBITS_NUM_BITS};
 use ckb_constant::hardfork::{mainnet, testnet};
 use ckb_crypto::secp::Privkey;
 use ckb_hash::{blake2b_256, new_blake2b};
@@ -554,10 +554,72 @@ impl ChainSpec {
         }
     }
 
+    fn validate_params(&self) -> Result<(), Box<dyn Error>> {
+        let genesis_epoch_length = self.params.genesis_epoch_length();
+        if genesis_epoch_length == 0 {
+            return Err(Box::new(SpecError::InvalidParams(
+                "genesis_epoch_length must be non-zero".to_string(),
+            )));
+        }
+
+        if self.params.epoch_duration_target() == 0 {
+            return Err(Box::new(SpecError::InvalidParams(
+                "epoch_duration_target must be non-zero".to_string(),
+            )));
+        }
+
+        let orphan_rate_target = self.params.orphan_rate_target();
+        if orphan_rate_target.1 == 0 {
+            return Err(Box::new(SpecError::InvalidParams(
+                "orphan_rate_target denominator must be non-zero".to_string(),
+            )));
+        }
+
+        let genesis_orphan_count = genesis_epoch_length
+            .checked_mul(u64::from(orphan_rate_target.0))
+            .ok_or_else(|| {
+                Box::new(SpecError::InvalidParams(
+                    "genesis_epoch_length * orphan_rate_target numerator overflows".to_string(),
+                )) as Box<dyn Error>
+            })?
+            / u64::from(orphan_rate_target.1);
+
+        genesis_epoch_length
+            .checked_add(genesis_orphan_count)
+            .ok_or_else(|| {
+                Box::new(SpecError::InvalidParams(
+                    "genesis_epoch_length + genesis_orphan_count overflows".to_string(),
+                )) as Box<dyn Error>
+            })?;
+
+        if let Some(deployments) = self.softfork_deployments() {
+            for (pos, deployment) in deployments {
+                if u32::from(deployment.bit) >= VERSIONBITS_NUM_BITS {
+                    return Err(Box::new(SpecError::InvalidParams(format!(
+                        "{pos} deployment bit must be less than {VERSIONBITS_NUM_BITS}"
+                    ))));
+                }
+                if deployment.period == 0 {
+                    return Err(Box::new(SpecError::InvalidParams(format!(
+                        "{pos} deployment period must be non-zero"
+                    ))));
+                }
+                if deployment.threshold.denom() == 0 {
+                    return Err(Box::new(SpecError::InvalidParams(format!(
+                        "{pos} deployment threshold denominator must be non-zero"
+                    ))));
+                }
+            }
+        }
+
+        Ok(())
+    }
+
     /// Build consensus instance
     ///
     /// [Consensus](consensus/struct.Consensus.html)
     pub fn build_consensus(&self) -> Result<Consensus, Box<dyn Error>> {
+        self.validate_params()?;
         let hardfork_switch = self.build_hardfork_switch()?;
         let genesis_epoch_ext = build_genesis_epoch_ext(
             self.params.initial_primary_epoch_reward(),
@@ -602,6 +664,7 @@ impl ChainSpec {
 
     /// Build genesis block from chain spec
     pub fn build_genesis(&self) -> Result<BlockView, Box<dyn Error>> {
+        self.validate_params()?;
         let special_cell_capacity = {
             let cellbase_transaction_for_special_cell_capacity =
                 self.build_cellbase_transaction(capacity_bytes!(500))?;
```

### spec/src/tests/mod.rs
```diff
@@ -227,6 +227,70 @@ fn test_default_params() {
     assert_eq!(params, expected);
 }
 
+#[test]
+fn test_invalid_consensus_params_are_rejected() {
+    fn assert_invalid_params(mut spec: ChainSpec, params: Params, expected: &str) {
+        spec.params = params;
+        let err = match spec.build_consensus() {
+            Ok(_) => panic!("invalid params were accepted"),
+            Err(err) => err,
+        };
+        assert!(
+            err.to_string().contains(expected),
+            "unexpected error: {err}"
+        );
+    }
+
+    let spec = load_spec_by_name("ckb_dev");
+
+    assert_invalid_params(
+        spec.clone(),
+        Params {
+            genesis_epoch_length: Some(0),
+            ..Default::default()
+        },
+        "genesis_epoch_length must be non-zero",
+    );
+
+    assert_invalid_params(
+        spec.clone(),
+        Params {
+            epoch_duration_target: Some(0),
+            ..Default::default()
+        },
+        "epoch_duration_target must be non-zero",
+    );
+
+    assert_invalid_params(
+        spec.clone(),
+        Params {
+            orphan_rate_target: Some((1, 0)),
+            ..Default::default()
+        },
+        "orphan_rate_target denominator must be non-zero",
+    );
+
+    assert_invalid_params(
+        spec.clone(),
+        Params {
+            genesis_epoch_length: Some(u64::MAX),
+            orphan_rate_target: Some((u32::MAX, 1)),
+            ..Default::default()
+        },
+        "genesis_epoch_length * orphan_rate_target numerator overflows",
+    );
+
+    assert_invalid_params(
+        spec,
+        Params {
+            genesis_epoch_length: Some(u64::MAX),
+            orphan_rate_target: Some((1, u32::MAX)),
+            ..Default::default()
+        },
+        "genesis_epoch_length + genesis_orphan_count overflows",
+    );
+}
+
 #[test]
 fn test_params_skip_serializing_if_option_is_none() {
     let default = Params::default();
```

### spec/src/versionbits/mod.rs
```diff
@@ -420,7 +420,11 @@ impl<'a> Versionbits<'a> {
 
     /// return bit mask corresponding deployment
     pub fn mask(&self) -> u32 {
-        1u32 << self.deployment().bit as u32
+        let bit = u32::from(self.deployment().bit);
+        debug_assert!(bit < VERSIONBITS_NUM_BITS);
+        1u32.checked_shl(bit)
+            .filter(|_| bit < VERSIONBITS_NUM_BITS)
+            .unwrap_or(0)
     }
 }
 
```

### sync/src/relayer/block_proposal_process.rs
```diff
@@ -24,14 +24,19 @@ impl<'a> BlockProposalProcess<'a> {
         );
         {
             let block_proposals = self.message;
-            let limit = shared.consensus().max_block_proposals_limit()
-                * (shared.consensus().max_uncles_num() as u64);
+            let max_block_proposals_limit = shared.consensus().max_block_proposals_limit();
+            let max_uncles_num = shared.consensus().max_uncles_num() as u64;
+            let Some(limit) = max_block_proposals_limit.checked_mul(max_uncles_num) else {
+                return StatusCode::ProtocolMessageIsMalformed.with_context(format!(
+                    "consensus max_block_proposals_limit({max_block_proposals_limit}) * max_uncles_num({max_uncles_num}) overflows"
+                ));
+            };
             if (block_proposals.transactions().len() as u64) > limit {
                 return StatusCode::ProtocolMessageIsMalformed.with_context(format!(
                     "Transactions count({}) > consensus max_block_proposals_limit({}) * max_uncles_num({})",
                     block_proposals.transactions().len(),
-                    shared.consensus().max_block_proposals_limit(),
-                    shared.consensus().max_uncles_num(),
+                    max_block_proposals_limit,
+                    max_uncles_num,
                 ));
             }
         }
```

### sync/src/relayer/get_block_proposal_process.rs
```diff
@@ -35,8 +35,13 @@ impl<'a> GetBlockProposalProcess<'a> {
         {
             // The block proposal request is separate from uncles,
             // so here the limit is only used to calculate the maximum value of uncles
-            let limit = shared.consensus().max_block_proposals_limit()
-                * (shared.consensus().max_uncles_num() as u64);
+            let max_block_proposals_limit = shared.consensus().max_block_proposals_limit();
+            let max_uncles_num = shared.consensus().max_uncles_num() as u64;
+            let Some(limit) = max_block_proposals_limit.checked_mul(max_uncles_num) else {
+                return StatusCode::ProtocolMessageIsMalformed.with_context(format!(
+                    "consensus max_block_proposals_limit({max_block_proposals_limit}) * max_uncles_num({max_uncles_num}) overflows"
+                ));
+            };
             if message_len as u64 > limit {
                 return StatusCode::ProtocolMessageIsMalformed.with_context(format!(
                     "GetBlockProposal proposals count({message_len}) > consensus max_block_proposals_limit({limit})"
```

### sync/src/synchronizer/mod.rs
```diff
@@ -603,7 +603,7 @@ impl Synchronizer {
                     // that for the first time, OR this peer was able to catch up to some earlier point
                     // where we checked against our tip.
                     // Either way, set a new timeout based on current tip.
-                    state.chain_sync.timeout = now + CHAIN_SYNC_TIMEOUT;
+                    state.chain_sync.timeout = now.saturating_add(CHAIN_SYNC_TIMEOUT);
                     state.chain_sync.work_header = Some(tip_header);
                     state.chain_sync.total_difficulty = Some(local_total_difficulty);
                     state.chain_sync.sent_getheaders = false;
@@ -621,7 +621,8 @@ impl Synchronizer {
                         }
                     } else {
                         state.chain_sync.sent_getheaders = true;
-                        state.chain_sync.timeout = now + EVICTION_HEADERS_RESPONSE_TIME;
+                        state.chain_sync.timeout =
+                            now.saturating_add(EVICTION_HEADERS_RESPONSE_TIME);
                         active_chain.send_getheaders_to_peer(
                             nc,
                             *peer,
```

### sync/src/types/mod.rs
```diff
@@ -101,7 +101,8 @@ impl ChainSyncState {
     fn tip_synced(&mut self) {
         let now = unix_time_as_millis();
         let avg_interval = (MAX_BLOCK_INTERVAL + MIN_BLOCK_INTERVAL) / 2;
-        self.headers_sync_state = HeadersSyncState::TipSynced(now + avg_interval * 1000);
+        self.headers_sync_state =
+            HeadersSyncState::TipSynced(now.saturating_add(avg_interval.saturating_mul(1000)));
     }
 
     fn started(&self) -> bool {
@@ -301,7 +302,7 @@ impl PeerState {
 
     fn suspend_sync(&mut self, suspend_time: u64) {
         let now = unix_time_as_millis();
-        self.chain_sync.suspend(now + suspend_time);
+        self.chain_sync.suspend(now.saturating_add(suspend_time));
         self.headers_sync_controller = None;
     }
 
@@ -362,7 +363,7 @@ impl<T: Eq + Hash + Clone> TtlFilter<T> {
             .inner
             .iter()
             .filter_map(|(key, time)| {
-                if *time + self.ttl < now {
+                if now.saturating_sub(*time) > self.ttl {
                     Some(key)
                 } else {
                     None
@@ -658,12 +659,12 @@ impl InflightBlocks {
         // we don't have to worry about missing points, and we don't need to
         // iterate through all the data each time, just check within tip + 20,
         // with the checkpoint marking possible blocking points, it's enough
-        let end = tip + 20;
+        let end = tip.saturating_add(20);
         for (key, value) in states.iter() {
             if key.number > end {
                 break;
             }
-            if value.timestamp + BLOCK_DOWNLOAD_TIMEOUT < now {
+            if now.saturating_sub(value.timestamp) > BLOCK_DOWNLOAD_TIMEOUT {
                 if let Some(set) = download_schedulers.get_mut(&value.peer) {
                     set.hashes.remove(key);
                     if should_punish && adjustment {
@@ -1365,7 +1366,7 @@ impl SyncState {
         pending.is_empty()
             || pending
                 .get(hash)
-                .map(|(_, _, time)| now > time + 2000)
+                .map(|(_, _, time)| now.saturating_sub(*time) > 2000)
                 .unwrap_or(true)
     }
 
@@ -1958,7 +1959,12 @@ impl ActiveChain {
             .write()
             .get(&(peer, block_number_and_hash.hash()))
         {
-            if Instant::now() < *last_time + GET_HEADERS_TIMEOUT {
+            let now = Instant::now();
+            if last_time
+                .checked_add(GET_HEADERS_TIMEOUT)
+                .map(|deadline| now < deadline)
+                .unwrap_or(true)
+            {
                 debug!(
                     "Last get_headers request to peer {} is less than {:?}; Ignore it.",
                     peer, GET_HEADERS_TIMEOUT,
```

### traits/src/epoch_provider.rs
```diff
@@ -17,7 +17,11 @@ pub trait EpochProvider {
     /// Get corresponding epoch progress information by block header
     fn get_block_epoch(&self, header: &HeaderView) -> Option<BlockEpoch> {
         self.get_epoch_ext(header).map(|epoch| {
-            if header.number() != epoch.start_number() + epoch.length() - 1 {
+            let tail_number = epoch
+                .start_number()
+                .checked_add(epoch.length())
+                .and_then(|number| number.checked_sub(1));
+            if Some(header.number()) != tail_number {
                 BlockEpoch::NonTailBlock { epoch }
             } else {
                 let last_block_hash_in_previous_epoch = if epoch.is_genesis() {
```

### tx-pool/src/component/orphan.rs
```diff
@@ -33,7 +33,9 @@ impl Entry {
             tx,
             peer,
             cycle,
-            expires_at: ckb_systemtime::unix_time().as_secs() + ORPHAN_TX_EXPIRE_TIME,
+            expires_at: ckb_systemtime::unix_time()
+                .as_secs()
+                .saturating_add(ORPHAN_TX_EXPIRE_TIME),
         }
     }
 }
```

### tx-pool/src/pool.rs
```diff
@@ -271,7 +271,7 @@ impl TxPool {
         let removed: Vec<_> = self
             .pool_map
             .iter()
-            .filter(|&entry| self.expiry + entry.inner.timestamp < now_ms)
+            .filter(|&entry| now_ms.saturating_sub(entry.inner.timestamp) > self.expiry)
             .map(|entry| entry.inner.clone())
             .collect();
 
```
