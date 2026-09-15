# [?] [dkg] Fix security and DoS issues in ChunkyDKG manager (#19544)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2026-04-28
Source: https://github.com/aptos-labs/aptos-core/commit/cc0d3a963c93c58045a5124bd94f68964fbad04b
Type: security-commit

## Details
[dkg] Fix security and DoS issues in ChunkyDKG manager (#19544)

* [dkg] Bind epoch into AggregatedSubtranscript signature to prevent cross-epoch replay

The AggregatedSubtranscript (which validators sign during certification)
did not include the epoch, allowing a valid multi-sig from epoch N to be
replayed in epoch N+1 if the validator set overlaps. Add dealer_epoch to
AggregatedSubtranscript so the BCS hash (and thus the signature) is
epoch-dependent. Also verify dealer_epoch matches metadata.epoch in the
VM execution path.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* [dkg] Replace Vec<Player> with BitVec for dealer sets in AggregatedSubtranscript

Vec<Player> allowed duplicates, reordering, and inflation of the dealer
list, which could produce malformed signatures or enable DoS via inflated
lists triggering expensive aggregation. Replace with BitVec (bitmask over
validator indices), which inherently prevents duplicates, enforces
canonical order, and bounds size to num_validators bits — matching the
existing AggregateSignature pattern. Validation on receipt is now just
bitmask length and popcount checks.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* [dkg] Harden ChunkyDKG signature request handling: state, rate-limit, spawn_blocking

- Accept signature requests in Finished state (not just
  AwaitAggregatedSubtranscriptCertification), so validators continue
  helping peers after completing their own DKG.
- Rate-limit to one concurrent handler per sender (previously only
  deduplicated same-hash retries, allowing different-hash spam).
- Move CPU-heavy subtranscript aggregation into spawn_blocking to
  avoid blocking the async runtime.
- Refactor handle_subtranscript_signature_request into focused helpers:
  resolve_subtranscripts (bitmask validation, local check, polling,
  fetching) and aggregate_and_sign (aggregation + hash verification +
  signing in spawn_blocking).
- Add quorum check: reject signature requests where the dealer set
  does not meet supermajority voting power.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
Made-with: Cursor

* [dkg] Inline ChunkyDKGSession::deal and consolidate transcript validation

- Remove the thin `ChunkyDKGSession::deal` wrapper; callers now invoke
  `ChunkyTranscript::deal` directly with explicit parameters.
- Delete `dkg/src/chunky/validation.rs`; merge its logic into
  `common::deserialize_chunky_transcript_and_verify` with an improved
  doc comment and internalized RNG creation.
- Update all call sites: dkg_manager, agg_subtrx_producer,
  missing_transcript_fetcher, and test_utils.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
Made-with: Cursor

* [dkg] Harden error handling: replace expect/debug_assert with Result propagation

- SubtranscriptProjective::aggregate_with: replace debug_assert_eq!
  with ensure! to prevent silent data corruption in release builds;
  include lengths in error messages.
- agg_subtrx_producer: replace expect() with ok_or_else() for peer
  power lookup and contributor lookups.
- agg_subtrx_producer: skip aggregation after quorum is met (early
  return when agg_subtrx_tx is already taken).
- agg_subtrx_producer: single-pass bitmask and hash collection with
  proper error propagation instead of expect().

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
Made-with: Cursor

* [dkg] Pre-compute subtranscript hash in certification state

Cache expected_subtranscript_hash in ChunkySubtranscriptCertificationState
at construction time to avoid repeated hashing on every signature
response. Rename field from subtranscript_hash to
expected_subtranscript_hash for clarity against the incoming response
field.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
Made-with: Cursor

* [dkg] Harden error handling: replace expect/debug_assert with Result propagation

- Fix post-quorum contributor tracking: move contributors.insert()
  before the aggregation skip guard so post-quorum senders are tracked,
  dedup works on retries, and ReliableBroadcast terminates.
- Replace expect() with Result propagation in bitmask validation to
  avoid panic on untrusted input.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

---------

Co-authored-by: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

### Cargo.lock
```diff
@@ -1435,6 +1435,7 @@ name = "aptos-dkg-runtime"
 version = "0.1.0"
 dependencies = [
  "anyhow",
+ "aptos-bitvec",
  "aptos-bounded-executor",
  "aptos-channels",
  "aptos-config",
```

### aptos-move/aptos-vm/src/validator_txns/chunky_dkg.rs
```diff
@@ -140,6 +140,9 @@ impl AptosVM {
         let trx: AggregatedSubtranscript = bcs::from_bytes(&transcript_bytes).map_err(|_| {
             ExecutionFailure::Expected(ExpectedFailure::TranscriptDeserializationFailed)
         })?;
+        if trx.dealer_epoch != metadata.epoch {
+            return Err(ExecutionFailure::Expected(ExpectedFailure::EpochNotCurrent));
+        }
         verifier
             .verify_multi_signatures(&trx, &signature)
             .map_err(|_| ExecutionFailure::Expected(ExpectedFailure::MultiSigVerificationFailed))?;
```

### crates/aptos-dkg/src/pvss/chunky/subtranscript.rs
```diff
@@ -12,6 +12,7 @@ use crate::{
     traits::{transcript::Aggregated, Aggregatable, TranscriptCore},
     Scalar,
 };
+use anyhow::ensure;
 use aptos_crypto::{
     arkworks::{
         random::{unsafe_random_point, unsafe_random_points},
@@ -165,18 +166,48 @@ impl<E: Pairing> Aggregated<Subtranscript<E>> for SubtranscriptProjective<E> {
         sc: &WeightedConfigArkworks<E::ScalarField>,
         other: &Subtranscript<E>,
     ) -> anyhow::Result<()> {
-        debug_assert_eq!(self.Cs_proj.len(), sc.get_total_num_players());
-        debug_assert_eq!(self.Vs_proj.len(), sc.get_total_num_players());
-        debug_assert_eq!(self.Cs_proj.len(), other.Cs.len());
-        debug_assert_eq!(self.Rs_proj.len(), other.Rs.len());
-        debug_assert_eq!(self.Vs_proj.len(), other.Vs.len());
+        ensure!(
+            self.Cs_proj.len() == sc.get_total_num_players(),
+            "Cs_proj length {} != num_players {}",
+            self.Cs_proj.len(),
+            sc.get_total_num_players()
+        );
+        ensure!(
+            self.Vs_proj.len() == sc.get_total_num_players(),
+            "Vs_proj length {} != num_players {}",
+            self.Vs_proj.len(),
+            sc.get_total_num_players()
+        );
+        ensure!(
+            self.Cs_proj.len() == other.Cs.len(),
+            "Cs_proj length {} != other {}",
+            self.Cs_proj.len(),
+            other.Cs.len()
+        );
+        ensure!(
+            self.Rs_proj.len() == other.Rs.len(),
+            "Rs_proj length {} != other {}",
+            self.Rs_proj.len(),
+            other.Rs.len()
+        );
+        ensure!(
+            self.Vs_proj.len() == other.Vs.len(),
+            "Vs_proj length {} != other {}",
+            self.Vs_proj.len(),
+            other.Vs.len()
+        );
 
         // Aggregate the V0s
         self.V0_proj += other.V0;
 
         // Aggregate Vs (nested) element-wise
         for (vs_row, other_row) in self.Vs_proj.iter_mut().zip(&other.Vs) {
-            debug_assert_eq!(vs_row.len(), other_row.len());
+            ensure!(
+                vs_row.len() == other_row.len(),
+                "Vs row length {} != other {}",
+                vs_row.len(),
+                other_row.len()
+            );
             for (v_ij, other_v_ij) in vs_row.iter_mut().zip(other_row) {
                 *v_ij += *other_v_ij;
             }
```

### dkg/Cargo.toml
```diff
@@ -14,6 +14,7 @@ rust-version = { workspace = true }
 
 [dependencies]
 anyhow = { workspace = true }
+aptos-bitvec = { workspace = true }
 aptos-bounded-executor = { workspace = true }
 aptos-channels = { workspace = true }
 aptos-config = { workspace = true }
```

### dkg/src/chunky/agg_subtrx_producer.rs
```diff
@@ -3,22 +3,20 @@
 
 use crate::{
     chunky::{
+        common::deserialize_chunky_transcript_and_verify,
         types::{
             AggregatedSubtranscriptWithHashes, ChunkyDKGTranscriptRequest, ChunkyTranscriptWithHash,
         },
-        validation::validate_chunky_transcript,
     },
     counters,
     types::DKGMessage,
 };
-use anyhow::{ensure, Context};
+use anyhow::{anyhow, ensure, Context};
+use aptos_bitvec::BitVec;
 use aptos_channels::aptos_channel;
 use aptos_consensus_types::common::Author;
 use aptos_crypto::HashValue;
-use aptos_dkg::pvss::{
-    traits::transcript::{Aggregatable, Aggregated},
-    Player,
-};
+use aptos_dkg::pvss::traits::transcript::{Aggregatable, Aggregated};
 use aptos_infallible::RwLock;
 use aptos_logger::info;
 use aptos_reliable_broadcast::{BroadcastStatus, ReliableBroadcast};
@@ -156,22 +154,21 @@ impl ChunkyTranscriptAggregationState {
             "[ChunkyDKG] adding peer chunky transcript failed with node author mismatch"
         );
 
-        let peer_power = self.epoch_state.verifier.get_voting_power(&sender);
-        ensure!(
-            peer_power.is_some(),
-            "[ChunkyDKG] adding peer chunky transcript failed with illegal dealer"
-        );
-        let peer_power = peer_power.expect("Peer must be valid");
+        let peer_power = self
+            .epoch_state
+            .verifier
+            .get_voting_power(&sender)
+            .ok_or_else(|| {
+                anyhow!("[ChunkyDKG] adding peer chunky transcript failed with illegal dealer")
+            })?;
 
         // Shared validation: deserialize, verify, check dealer ID.
-        let mut rng = rand::thread_rng();
-        let transcript = validate_chunky_transcript(
+        let transcript = deserialize_chunky_transcript_and_verify(
             sender,
             transcript_bytes,
             &self.dkg_config,
             &self.signing_pubkeys,
             &self.epoch_state,
-            &mut rng,
         )?;
 
         Ok((transcript, peer_power))
@@ -202,7 +199,6 @@ impl BroadcastStatus<DKGMessage> for Arc<ChunkyTranscriptAggregationState> {
             }
         }
 
-        // RwLock allows concurrent validation of multiple transcripts
         let (transcript, peer_power) =
             self.validate_and_deserialize_transcript(sender, metadata, transcript_bytes)?;
 
@@ -233,9 +229,14 @@ impl BroadcastStatus<DKGMessage> for Arc<ChunkyTranscriptAggregationState> {
             received_transcripts.insert(metadata.author, transcript);
         }
 
-        // Aggregate the transcript (projective accumulator; normalize when quorum is met)
-        // TODO(ibalajiarun): Should the transcript be aggregated if quorum is already met?
         inner_state.contributors.insert(metadata.author);
+
+        // Quorum already reached — transcript is stored for the fetcher but no
+        // further aggregation is needed.
+        if inner_state.agg_subtrx_tx.is_none() {
+            let all_received = inner_state.contributors.len() >= self.epoch_state.verifier.len();
+            return Ok(all_received.then_some(()));
+        }
         if let Some(agg_subtrx) = inner_state.subtrx.as_mut() {
             agg_subtrx
                 .aggregate_with(&self.dkg_config.threshold_config, &subtranscript)
@@ -259,59 +260,51 @@ impl BroadcastStatus<DKGMessage> for Arc<ChunkyTranscriptAggregationState> {
 
         // Send to agg_subtrx_tx when quorum is met (only once)
         if quorum_met {
-            if let Some(tx) = inner_state.agg_subtrx_tx.take() {
-                let agg_trx = inner_state.subtrx.take().unwrap().normalize();
-                // Convert AccountAddress contributors to Player by getting their validator indices.
-                // Sort by AccountAddress so dealers order is deterministic (HashSet iteration is
-                // non-deterministic); AggregatedSubtranscript is BCSCryptoHash'd for certification.
-                let mut contributors: Vec<_> = inner_state.contributors.iter().copied().collect();
-                contributors.sort();
-                let dealers: Vec<Player> = contributors
-                    .iter()
-                    .map(|addr| {
-                        self.epoch_state
-                            .verifier
-                            .address_to_validator_index()
-                            .get(addr)
-                            .map(|&index| Player { id: index })
-                            .expect("Request must be sent to validators in current set only")
-                    })
-                    .collect();
-                // Compute per-dealer transcript hashes in the same order as dealers.
-                // These are included in the signature request so the responder can detect
-                // equivocated transcripts (where a dealer sent different transcripts to
-                // different validators), not just missing ones.
-                let dealer_transcript_hashes: Vec<HashValue> = {
-                    let received = self.received_transcripts.read();
-                    contributors
-                        .iter()
-                        .map(|addr| {
-                            let twh = received
-                                .get(addr)
-                                .expect("contributor must have a stored transcript");
-                            twh.hash()
-                        })
-                        .collect()
-                };
-                let agg_subtrx = AggregatedSubtranscript {
+            let tx = inner_state
+                .agg_subtrx_tx
+                .take()
+                .expect("agg_subtrx_tx must be Some due to early return above");
+            let agg_trx = inner_state.subtrx.take().unwrap().normalize();
+            let num_validators = self.epoch_state.verifier.len();
+            let addr_to_index = self.epoch_state.verifier.address_to_validator_index();
+            let received = self.received_transcripts.read();
+
+            let mut dealer_bitmask = BitVec::with_num_bits(num_validators as u16);
+            let mut indexed_hashes: Vec<(usize, HashValue)> = Vec::new();
+            for addr in inner_state.contributors.iter() {
+                let index = *addr_to_index
+                    .get(addr)
+                    .ok_or_else(|| anyhow!("contributor {} not in validator set", addr))?;
+                dealer_bitmask.set(index as u16);
+                let hash = received
+                    .get(addr)
+                    .ok_or_else(|| anyhow!("contributor {} missing stored transcript", addr))?
+                    .hash();
+                indexed_hashes.push((index, hash));
+            }
+            indexed_hashes.sort_by_key(|(idx, _)| *idx);
+            let dealer_transcript_hashes: Vec<HashValue> =
+                indexed_hashes.into_iter().map(|(_, h)| h).collect();
+            drop(received);
+
+            let with_hashes = AggregatedSubtranscriptWithHashes {
+                aggregated_subtranscript: AggregatedSubtranscript {
+                    dealer_epoch: self.dkg_config.session_metadata.dealer_epoch,
                     subtranscript: agg_trx,
-                    dealers,
-                };
-                let with_hashes = AggregatedSubtranscriptWithHashes {
-                    aggregated_subtranscript: agg_subtrx,
-                    dealer_transcript_hashes,
-                };
-                if let Err(e) = tx.push((), with_hashes) {
-                    info!(
-                        epoch = epoch,
-                        "[ChunkyDKG] Failed to send aggregated chunky transcript to ChunkyDKGManager when quorum met: {:?}", e
-                    );
-                } else {
-                    info!(
-                        epoch = epoch,
-                        "[ChunkyDKG] sent aggregated chunky transcript to ChunkyDKGManager (quorum met)"
-                    );
-                }
+                    dealer_bitmask,
+                },
+                dealer_transcript_hashes,
+            };
+            if let Err(e) = tx.push((), with_hashes) {
+                info!(
+                    epoch = epoch,
+                    "[ChunkyDKG] Failed to send aggregated chunky transcript to ChunkyDKGManager when quorum met: {:?}", e
+                );
+            } else {
+                info!(
+                    epoch = epoch,
+                    "[ChunkyDKG] sent aggregated chunky transcript to ChunkyDKGManager (quorum met)"
+                );
             }
         }
 
@@ -403,8 +396,13 @@ mod tests {
         let agg = rx.select_next_some().now_or_never();
         assert!(agg.is_some());
         let agg_with_hashes = agg.unwrap();
-        // Dealers should be sorted by AccountAddress, then mapped to validator indices.
-        assert_eq!(agg_with_hashes.aggregated_subtranscript.dealers.len(), 3);
+        assert_eq!(
+            agg_with_hashes
+                .aggregated_subtranscript
+                .dealer_bitmask
+                .count_ones(),
+            3
+        );
         assert_eq!(agg_with_hashes.dealer_transcript_hashes.len(), 3);
 
         // Fourth transcript — all received, returns Some(()).
@@ -480,7 +478,13 @@ mod tests {
         let agg = rx.select_next_some().now_or_never();
         assert!(agg.is_some());
         let agg_with_hashes = agg.unwrap();
-        assert_eq!(agg_with_hashes.aggregated_subtranscript.dealers.len(), 1);
+        assert_eq!(
+            agg_with_hashes
+                .aggregated_subtranscript
+                .dealer_bitmask
+                .count_ones(),
+            1
+        );
         assert_eq!(agg_with_hashes.dealer_transcript_hashes.len(), 1);
     }
 }
```

### dkg/src/chunky/common.rs
```diff
@@ -10,21 +10,19 @@ use aptos_types::{
     epoch_state::EpochState,
 };
 use move_core_types::account_address::AccountAddress;
-use rand::{CryptoRng, RngCore};
 
 /// Shared transcript validation pipeline used by both the aggregation producer and the
 /// transcript fetcher. Deserializes, cryptographically verifies, and checks dealer ID.
 ///
-/// The transcript is cryptographically verified via `transcript.verify()` which checks the
-/// dealer's key pair; the dealer-ID check ensures it belongs to the expected dealer; envelope
-/// metadata (epoch, author) is validated by the caller as belt-and-suspenders.
-pub fn validate_chunky_transcript<R: RngCore + CryptoRng>(
+/// `transcript.verify()` checks the PVSS proof and dealer signature against the full session
+/// parameters; the dealer-ID check ensures the transcript belongs to the expected sender;
+/// envelope metadata (epoch, author) is validated by the caller.
+pub fn deserialize_chunky_transcript_and_verify(
     sender: AccountAddress,
     transcript_bytes: &[u8],
     dkg_config: &ChunkyDKGSession,
     signing_pubkeys: &[DealerPublicKey],
     epoch_state: &EpochState,
-    rng: &mut R,
 ) -> anyhow::Result<ChunkyTranscriptWithHash> {
     // Hash the canonical BCS wire bytes once up front to avoid repeated re-serialization.
     // Safe because BCS is strictly canonical: deserialize(serialize(x)) == x byte-for-byte.
@@ -40,6 +38,7 @@ pub fn validate_chunky_transcript<R: RngCore + CryptoRng>(
     let transcript: ChunkyTranscript = bcs::from_bytes(transcript_bytes)
         .map_err(|e| anyhow!("[ChunkyDKG] Unable to deserialize chunky transcript: {e}"))?;
 
+    let mut rng = rand::thread_rng();
     // Verify the transcript cryptographically.
     monitor!(
         "chunky_validate_transcript_verify",
@@ -49,7 +48,7 @@ pub fn validate_chunky_transcript<R: RngCore + CryptoRng>(
             signing_pubkeys,
             &dkg_config.eks,
             &dkg_config.session_metadata,
-            rng,
+            &mut rng,
         )
     )
     .context("chunky transcript verification failed")?;
```

### dkg/src/chunky/dkg_manager/mod.rs
```diff
@@ -19,8 +19,11 @@ use crate::{
 };
 use anyhow::{anyhow, bail, ensure, Context, Result};
 use aptos_channels::{aptos_channel, message_queues::QueueStyle};
-use aptos_crypto::{hash::CryptoHash, HashValue, SigningKey, Uniform};
-use aptos_dkg::pvss::{traits::transcript::Aggregatable, Player};
+use aptos_crypto::{bls12381, hash::CryptoHash, HashValue, SigningKey, Uniform};
+use aptos_dkg::pvss::{
+    traits::{transcript::Aggregatable, Transcript},
+    Player,
+};
 use aptos_infallible::{duration_since_epoch, RwLock};
 use aptos_logger::{debug, error, info, warn};
 use aptos_reliable_broadcast::{DropGuard, ReliableBroadcast};
@@ -30,7 +33,7 @@ use aptos_types::{
             AggregatedSubtranscript, CertifiedAggregatedChunkySubtranscript,
             CertifiedChunkyDKGOutput, ChunkyDKGSession, ChunkyDKGSessionMetadata,
             ChunkyDKGSessionState, ChunkyDKGStartEvent, ChunkyDKGTranscript, ChunkyInputSecret,
-            ChunkySubtranscript, DealerPrivateKey, DealerPublicKey,
+            ChunkySubtranscript, ChunkyTranscript, DealerPrivateKey, DealerPublicKey,
         },
         DKGTranscriptMetadata,
     },
@@ -86,6 +89,8 @@ enum InnerState {
         vtxn_guard: TxnGuard,
         start_time: Duration,
         my_transcript: Arc<ChunkyDKGTranscript>,
+        aggregated_subtranscript: Arc<AggregatedSubtranscript>,
+        dkg_config: Arc<ChunkyDKGSession>,
         proposed: bool,
     },
 }
@@ -391,27 +396,31 @@ impl ChunkyDKGManager {
             "[ChunkyDKG] Deal transcript started.",
         );
 
-        let dkg_config = ChunkyDKGSession::new(dkg_session_metadata);
-        let dkg_config_clone = dkg_config.clone();
+        let session = ChunkyDKGSession::new(dkg_session_metadata);
+
+        let session_clone = session.clone();
         let ssk_clone = self.ssk.clone();
         let spk_clone = self.spk.clone();
         let my_index = self.my_index;
-        let dkg_session_metadata_clone = dkg_session_metadata.clone();
 
         let trx = tokio::task::spawn_blocking(move || {
             let mut rng = StdRng::from_rng(thread_rng()).unwrap();
             let input_secret = ChunkyInputSecret::generate(&mut rng);
-
             let dealer = Player { id: my_index };
-            let session_id = dkg_session_metadata_clone;
-
-            dkg_config_clone.deal(
-                &ssk_clone,
-                &spk_clone,
-                &input_secret,
-                &session_id,
-                &dealer,
-                &mut rng,
+
+            monitor!(
+                "chunky_dkg_deal_transcript",
+                ChunkyTranscript::deal(
+                    &session_clone.threshold_config,
+                    &session_clone.public_parameters,
+                    &ssk_clone,
+                    &spk_clone,
+                    &session_clone.eks,
+                    &input_secret,
+                    &session_clone.session_metadata,
+                    &dealer,
+                    &mut rng,
+                )
             )
         })
         .await?;
@@ -421,6 +430,7 @@ impl ChunkyDKGManager {
         counters::CHUNKY_DKG_OBJECT_SIZE_BYTES
             .with_label_values(&["dealer_transcript"])
             .observe(transcript_bytes.len() as f64);
+
         let my_transcript = Arc::new(ChunkyDKGTranscript::new(
             self.epoch_state.epoch,
             self.my_addr,
@@ -449,7 +459,7 @@ impl ChunkyDKGManager {
             self.reliable_broadcast.clone(),
             self.epoch_state.clone(),
             self.my_addr,
-            dkg_config.clone(),
+            session.clone(),
             spks,
             dkg_start_time,
             self.agg_subtrx_tx.as_ref().cloned(),
@@ -461,7 +471,7 @@ impl ChunkyDKGManager {
             start_time: dkg_start_time,
             my_transcript,
             _abort_guard: DropGuard::new(abort_handle),
-            dkg_config,
+            dkg_config: session,
         };
 
         Ok(())
@@ -542,6 +552,8 @@ impl ChunkyDKGManager {
         let InnerState::AwaitAggregatedSubtranscriptCertification {
             start_time,
             my_transcript,
+            aggregated_subtranscript: local_agg_subtrx,
+            dkg_config,
             ..
         } = mem::take(&mut self.state)
         else {
@@ -558,12 +570,13 @@ impl ChunkyDKGManager {
         info!("[ChunkyDKG] deriving encryption key");
         // Derive encryption key from subtranscript + DigestKey.
         // Heavy pairing-based crypto — run off the main loop.
+        let agg_subtrx_for_blocking = Arc::clone(&aggregated_subtranscript);
         let (encryption_key_bytes, transcript_bytes) = tokio::task::spawn_blocking(move || {
             let digest_key = DIGEST_KEY
                 .as_ref()
                 .ok_or_else(|| anyhow!("DigestKey not available; cannot derive encryption key"))?;
-            let key = aggregated_subtranscript.derive_encryption_key_bytes(digest_key.tau_g2)?;
-            let bytes = bcs::to_bytes(&aggregated_subtranscript)
+            let key = agg_subtrx_for_blocking.derive_encryption_key_bytes(digest_key.tau_g2)?;
+            let bytes = bcs::to_bytes(agg_subtrx_for_blocking.as_ref())
                 .map_err(|e| anyhow!("transcript serialization error: {e}"))?;
             counters::CHUNKY_DKG_OBJECT_SIZE_BYTES
                 .with_label_values(&["aggregated_subtranscript"])
@@ -604,10 +617,13 @@ impl ChunkyDKGManager {
             my_addr = self.my_addr,
             "[ChunkyDKG] aggregated transcript put into vtxn pool."
         );
+        let _ = local_agg_subtrx;
         self.state = InnerState::Finished {
             vtxn_guard,
             start_time,
             my_transcript,
+            aggregated_subtranscript,
+            dkg_config,
             proposed: false,
         };
         Ok(())
@@ -756,14 +772,16 @@ impl ChunkyDKGManager {
     ) -> Result<()> {
         let (aggregated_transcript, dkg_config) = match &self.state {
             InnerState::AwaitAggregatedSubtranscriptCertification {
-                aggregated_subtranscript: aggregated_transcript,
+                aggregated_subtranscript,
+                dkg_config,
+                ..
+            }
+            | InnerState::Finished {
+                aggregated_subtranscript,
                 dkg_config,
                 ..
-            } => (Arc::clone(aggregated_transcript), Arc::clone(dkg_config)),
+            } => (Arc::clone(aggregated_subtranscript), Arc::clone(dkg_config)),
             _ => {
-                // Send error response instead of dropping response_sender.
-                // Drop = timeout = exponential backoff blowup on the requester side.
-                // Error = quick retry.
                 response_sender.send(Err(anyhow!(
                     "[ChunkyDKG] not ready for signature requests in state {:?}",
                     self.state.variant_name()
@@ -774,13 +792,11 @@ impl ChunkyDKGManager {
 
         let req_subtranscript_hash = req.subtranscript_hash;
 
-        // Skip-if-running: if a handler for this sender with the same subtranscript_hash
-        // is still running, skip spawning a new one. This prevents ReliableBroadcast retries
-        // from aborting a handler that is sleeping (delay+poll) or fetching.
-        // Two-level if: keeps pattern binding separate from boolean guard for readability.
-        #[allow(clippy::collapsible_if)]
-        if let Some((existing_hash, handle)) = self.rpc_handler_guards.get(&sender) {
-            if *existing_hash == req.subtranscript_hash && !handle.is_finished() {
+        // Rate limit: at most one concurrent handler per sender. This prevents
+        // a malicious validator from spawning many expensive handlers by varying
+        // the subtranscript hash. Also deduplicates ReliableBroadcast retries.
+        if let Some((_existing_hash, handle)) = self.rpc_handler_guards.get(&sender) {
+            if !handle.is_finished() {
                 counters::CHUNKY_DKG_SIGNATURE_REQUEST_SKIPPED.inc();
                 response_sender.send(Err(anyhow!(
                     "handler already in-flight for sender {}",
@@ -837,87 +853,63 @@ impl ChunkyDKGManager {
         Ok(())
     }
 
-    /// Detect mismatched or missing dealers by comparing per-dealer hashes against
-    /// the received transcripts map. Uses precomputed transcript hashes.
-    fn detect_mismatches(
-        dealer_addresses: &[AccountAddress],
-        expected_hashes: &[HashValue],
-        received_transcripts: &RwLock<HashMap<AccountAddress, ChunkyTranscriptWithHash>>,
-    ) -> Result<(Vec<ChunkySubtranscript>, Vec<AccountAddress>)> {
-        let map = received_transcripts.read();
-        let mut subtranscripts = Vec::new();
-        let mut mismatched = Vec::new();
-        for (i, addr) in dealer_addresses.iter().enumerate() {
-            match map.get(addr) {
-                Some(twh) => {
-                    if twh.hash() == expected_hashes[i] {
-                        subtranscripts.push(twh.get_subtranscript());
-                    } else {
-                        mismatched.push(*addr);
-                    }
-                },
-                None => mismatched.push(*addr),
-            }
-        }
-        Ok((subtranscripts, mismatched))
-    }
-
-    /// Handle subtranscript validation computation.
-    async fn handle_subtranscript_signature_request(
+    /// Resolve all subtranscripts required by a signature request: validate the bitmask,
+    /// check local storage, poll for late arrivals, and fetch any still-missing transcripts.
+    async fn resolve_subtranscripts(
         sender: AccountAddress,
-        req: ChunkyDKGSubtranscriptSignatureRequest,
-        local_aggregated_transcript: Arc<AggregatedSubtranscript>,
-        dkg_config: Arc<ChunkyDKGSession>,
-        ssk: Arc<DealerPrivateKey>,
-        _my_addr: AccountAddress,
-        received_transcripts: Arc<RwLock<HashMap<AccountAddress, ChunkyTranscriptWithHash>>>,
-        epoch_state: Arc<EpochState>,
+        req: &ChunkyDKGSubtranscriptSignatureRequest,
+        received_transcripts: &Arc<RwLock<HashMap<AccountAddress, ChunkyTranscriptWithHash>>>,
+        epoch_state: &Arc<EpochState>,
+        dkg_config: &Arc<ChunkyDKGSession>,
         network_sender: Arc<NetworkSender>,
-    ) -> Result<DKGMessage> {
-        // In the miniscule chance that the locally aggregated subtranscript is the same as the
-        // remote transcript, we can just sign and return immediately.
-        if local_aggregated_transcript.hash() == req.subtranscript_hash {
-            let signature = ssk
-                .sign(local_aggregated_transcript.as_ref())
-                .map_err(|e| anyhow!("failed to sign subtranscript validation: {:?}", e))?;
-
-            let response = DKGMessage::SubtranscriptSignatureResponse(
-                ChunkyDKGSubtranscriptSignatureResponse::new(
-                    req.dealer_epoch,
-                    req.subtranscript_hash,
-                    signature,
-                ),
-            );
-
-            return Ok(response);
-        }
-
-        // Convert Player dealers to AccountAddress using validator indices
-        let dealer_addresses: Vec<AccountAddress> = req
-            .aggregated_subtrx_dealers
-            .iter()
-            .filter_map(|player| {
-                epoch_state
-                    .verifier
-                    .get_ordered_account_addresses()
-                    .get(player.id)
-                    .copied()
-            })
-            .collect();
-        ensure!(dealer_addresses.len() == req.aggregated_subtrx_dealers.len());
+    ) -> Result<Vec<ChunkySubtranscript>> {
+        let num_validators = epoch_state.verifier.len();
+        let ordered_addrs = epoch_state.verifier.get_ordered_account_addresses();
+        let max_bit = req
+            .dealer_bitmask
+            .last_set_bit()
+            .ok_or_else(|| anyhow!("dealer_bitmask is empty"))?;
+        ensure!(
+            (max_bit as usize) < num_validators,
+            "dealer_bitmask contains out-of-range bits"
+        );
+        let num_dealers = req.dealer_bitmask.count_ones() as usize;
         ensure!(
-            req.dealer_transcript_hashes.len() == dealer_addresses.len(),
-            "dealer_transcript_hashes length mismatch with dealers"
+            req.dealer_transcript_hashes.len() == num_dealers,
+            "dealer_transcript_hashes length mismatch with dealer_bitmask popcount"
         );
 
-        // First check for mismatches.
-        let (mut subtranscripts, mismatched_dealers) = Self::detect_mismatches(
-            &dealer_addresses,
-            &req.dealer_transcript_hashes,
-            &received_transcripts,
-        )?;
+        // Safety: last_set_bit check above guarantees all indices are < num_validators.
+        let dealers: Vec<(AccountAddress, HashValue)> = req
+            .dealer_bitmask
+            .iter_ones()
+            .map(|idx| ordered_addrs[idx])
+            .zip(req.dealer_transcript_hashes.iter().copied())
+            .collect();
 
-        if !mismatched_dealers.is_empty() {
+        epoch_state
+            .verifier
+            .check_voting_power(dealers.iter().map(|(addr, _)| addr), true)
+            .map_err(|e| anyhow!("dealer set does not meet quorum: {:?}", e))?;
+
+        let check_local = || {
+            let map = received_transcripts.read();
+            let mut subtranscripts = Vec::new();
+            let mut missing = Vec::new();
+            for &(addr, expected_hash) in &dealers {
+                match map.get(&addr) {
+                    Some(twh) if twh.hash() == expected_hash => {
+                        subtranscripts.push(twh.get_subtranscript())
+                    },
+                    _ => missing.push(addr),
+                }
+            }
+            (subtranscripts, missing)
+        };
+
+        let (mut subtranscripts, missing_dealers) = check_local();
+
+        if !missing_dealers.is_empty() {
             // Poll received_transcripts to let the aggregator resolve mismatches.
             // Most of the time, the aggregator collects all needed transcripts
             // within this window, eliminating the need to fetch entirely.
@@ -931,43 +923,35 @@ impl ChunkyDKGManager {
             );
             let deadline = tokio::time::Instant::now() + MAX_WAIT + jitter;
 
-            let (mut fresh_subtranscripts, mut still_missing) =
-                (subtranscripts.clone(), mismatched_dealers.clone());
+            let mut still_missing = missing_dealers.clone();
             while tokio::time::Instant::now() < deadline {
                 tokio::time::sleep(POLL_INTERVAL).await;
-                let (s, m) = Self::detect_mismatches(
-                    &dealer_addresses,
-                    &req.dealer_transcript_hashes,
-                    &received_transcripts,
-                )?;
-                fresh_subtranscripts = s;
+                let (s, m) = check_local();
+                subtranscripts = s;
                 still_missing = m;
                 if still_missing.is_empty() {
                     break;
                 }
             }
-            subtranscripts = fresh_subtranscripts;
 
-            // Log how many mismatches the delay resolved.
-            let resolved = mismatched_dealers.len().saturating_sub(still_missing.len());
+            let resolved = missing_dealers.len().saturating_sub(still_missing.len());
             info!(
                 sender = sender,
-                initial_mismatches = mismatched_dealers.len(),
+                initial_mismatches = missing_dealers.len(),
                 resolved_by_delay = resolved,
                 still_missing = still_missing.len(),
                 "[ChunkyDKG] Post-delay recheck: {}/{} mismatches resolved by aggregator",
                 resolved,
-                mismatched_dealers.len(),
+                missing_dealers.len(),
             );
 
-            // Fetch only if still needed.
             if !still_missing.is_empty() {
                 let fetcher = TranscriptFetcher::new(
                     sender,
                     req.dealer_epoch,
                     still_missing,
                     Duration::from_secs(10),
-                    Arc::clone(&dkg_config),
+                    Arc::clone(dkg_config),
                     epoch_state.clone(),
                 );
                 let fetched = monitor!(
@@ -998,40 +982,94 @@ impl ChunkyDKGManager {
             "No transcripts found for required dealers"
         );
         ensure!(
-            subtranscripts.len() == dealer_addresses.len(),
+            subtranscripts.len() == num_dealers,
             "Not enough subtranscripts"
         );
 
-        // Aggregate subtranscripts in projective form, then normalize (same logic as chunky_agg_trx_producer)
-        let recomputed_subtranscript =
-            ChunkySubtranscript::aggregate(&dkg_config.threshold_config, subtranscripts)
-                .context("failed to aggregate subtranscripts")?;
-        let recomputed_aggsubtranscript = AggregatedSubtranscript {
-            subtranscript: recomputed_subtranscript,
-            dealers: req.aggregated_subtrx_dealers.clone(),
-        };
+        Ok(subtranscripts)
+    }
 
-        // Verify the hash matches
-        ensure!(
-            recomputed_aggsubtranscript.hash() == req.subtranscript_hash,
-            "subtranscript hash mismatch in validation request"
-        );
+    /// Aggregate resolved subtranscripts, verify the hash matches the request, and sign.
+    /// CPU-heavy work runs inside `spawn_blocking`.
+    async fn aggregate_and_sign(
+        subtranscripts: Vec<ChunkySubtranscript>,
+        req: &ChunkyDKGSubtranscriptSignatureRequest,
+        dkg_config: &ChunkyDKGSession,
+        ssk: &Arc<DealerPrivateKey>,
+    ) -> Result<(AggregatedSubtranscript, bls12381::Signature)> {
+        let dealer_epoch = req.dealer_epoch;
+        let dealer_bitmask = req.dealer_bitmask.clone();
+        let subtranscript_hash = req.subtranscript_hash;
+        let threshold_config = dkg_config.threshold_config.clone();
+        let ssk = Arc::clone(ssk);
+        tokio::task::spawn_blocking(move || {
+            let recomputed_subtranscript =
+                ChunkySubtranscript::aggregate(&threshold_config, subtranscripts)
+                    .context("failed to aggregate subtranscripts")?;
+            let recomputed = AggregatedSubtranscript {
+                dealer_epoch,
+                subtranscript: recomputed_subtranscript,
+                dealer_bitmask,
+            };
+            ensure!(
+                recomputed.hash() == subtranscript_hash,
+                "subtranscript hash mismatch in validation request"
+            );
+            let sig = ssk
+                .sign(&recomputed)
+                .map_err(|e| anyhow!("failed to sign subtranscript validation: {:?}", e))?;
+            Ok((recomputed, sig))
+        })
+        .await
+        .map_err(|e| anyhow!("spawn_blocking join error: {e}"))?
+    }
 
-        // Sign over the subtranscript hash
-        let signature = ssk
-            .sign(&recomputed_aggsubtranscript)
-            .map_err(|e| anyhow!("failed to sign subtranscript validation: {:?}", e))?;
+    /// Handle subtranscript validation computation.
+    async fn handle_subtranscript_signature_request(
+        sender: AccountAddress,
+        req: ChunkyDKGSubtranscriptSignatureRequest,
+        local_aggregated_transcript: Arc<AggregatedSubtranscript>,
+        dkg_config: Arc<ChunkyDKGSession>,
+        ssk: Arc<DealerPrivateKey>,
+        _my_addr: AccountAddress,
+        received_transcripts: Arc<RwLock<HashMap<AccountAddress, ChunkyTranscriptWithHash>>>,
+        epoch_state: Arc<EpochState>,
+        network_sender: Arc<NetworkSender>,
+    ) -> Result<DKGMessage> {
+        // Fast path: local aggregated transcript matches — sign and return immediately.
+        if local_aggregated_transcript.hash() == req.subtranscript_hash {
+            let signature = ssk
+                .sign(local_aggregated_transcript.as_ref())
+                .map_err(|e| anyhow!("failed to sign subtranscript validation: {:?}", e))?;
+            return Ok(DKGMessage::SubtranscriptSignatureResponse(
+                ChunkyDKGSubtranscriptSignatureResponse::new(
+                    req.dealer_epoch,
+                    req.subtranscript_hash,
+                    signature,
+                ),
+            ));
+        }
 
-        // Build and send a response message
-        let response = DKGMessage::SubtranscriptSignatureResponse(
+        let subtranscripts = Self::resolve_subtranscripts(
+            sender,
+            &req,
+            &received_transcripts,
+            &epoch_state,
+            &dkg_config,
+            network_sender,
+        )
+        .await?;
+
+        let (_recomputed, signature) =
+            Self::aggregate_and_sign(subtranscripts, &req, &dkg_config, &ssk).await?;
+
+        Ok(DKGMessage::SubtranscriptSignatureResponse(
             ChunkyDKGSubtranscriptSignatureResponse::new(
                 req.dealer_epoch,
                 req.subtranscript_hash,
                 signature,
             ),
-        );
-
-        Ok(response)
+        ))
     }
 
     #[cfg(test)]
```

### dkg/src/chunky/dkg_manager/tests.rs
```diff
@@ -5,13 +5,17 @@ use super::ChunkyDKGManager;
 use crate::{
     chunky::{
         test_utils::{ChunkyTestSetup, DummyNetworkSender},
-        types::{CertifiedAggregatedSubtranscript, MissingTranscriptRequest},
+        types::{
+            CertifiedAggregatedSubtranscript, ChunkyDKGSubtranscriptSignatureRequest,
+            MissingTranscriptRequest,
+        },
     },
     network::{DummyRpcResponseSender, IncomingRpcRequest},
     types::DKGMessage,
 };
+use aptos_bitvec::BitVec;
 use aptos_bounded_executor::BoundedExecutor;
-use aptos_crypto::SigningKey;
+use aptos_crypto::{HashValue, SigningKey};
 use aptos_infallible::RwLock;
 use aptos_network::{
     application::{interface::NetworkClient, storage::PeersAndMetadata},
@@ -290,3 +294,211 @@ async fn test_close_and_notifications() {
         .await;
     assert!(result.is_err());
 }
+
+fn new_signature_request_rpc(
+    epoch: u64,
+    sender: AccountAddress,
+    subtranscript_hash: HashValue,
+    dealer_bitmask: BitVec,
+    dealer_transcript_hashes: Vec<HashValue>,
+    response_collector: Arc<RwLock<Vec<anyhow::Result<DKGMessage>>>>,
+) -> IncomingRpcRequest {
+    IncomingRpcRequest {
+        msg: DKGMessage::SubtranscriptSignatureRequest(
+            ChunkyDKGSubtranscriptSignatureRequest::new(
+                epoch,
+                subtranscript_hash,
+                dealer_bitmask,
+                dealer_transcript_hashes,
+            ),
+        ),
+        sender,
+        response_sender: Box::new(DummyRpcResponseSender::new(response_collector)),
+    }
+}
+
+/// Helper: advance a manager through the full DKG lifecycle to Finished.
+async fn advance_to_finished(manager: &mut ChunkyDKGManager, setup: &ChunkyTestSetup) {
+    let event = ChunkyDKGStartEvent {
+        session_metadata: setup.session_metadata.clone(),
+        start_time_us: Duration::from_secs(1700000000).as_micros() as u64,
+    };
+    manager.process_dkg_start_event(event).await.unwrap();
+
+    let agg_with_hashes = setup.aggregate_subtranscripts_with_hashes(&[0, 1, 2]);
+    let agg_subtrx = agg_with_hashes.aggregated_subtranscript.clone();
+    manager
+        .process_aggregated_subtranscript(agg_with_hashes)
+        .await
+        .unwrap();
+
+    let mut sigs = std::collections::BTreeMap::new();
+    for i in 0..3 {
+        let sig = setup.private_keys[i].sign(&agg_subtrx).unwrap();
+        sigs.insert(setup.addrs[i], sig);
+    }
+    let aggregate_signature = setup
+        .epoch_state
+        .verifier
+        .aggregate_signatures(sigs.iter())
+        .unwrap();
+    let certified = CertifiedAggregatedSubtranscript {
+        aggregated_subtranscript: Arc::new(agg_subtrx),
+        aggregate_signature,
+    };
+    manager
+        .process_certified_aggregated_subtranscript(certified)
+        .await
+        .unwrap();
+    assert_eq!(manager.state_name(), "Finished");
+}
+
+#[tokio::test]
+async fn test_signature_request_accepted_in_finished_state() {
+    let setup = ChunkyTestSetup::new_uniform(4);
+    let mut manager = create_test_manager(&setup);
+    advance_to_finished(&mut manager, &setup).await;
+
+    // Build a signature request with a dummy hash — the handler will be spawned
+    // even though the hash won't match locally. The key test is that the request
+    // is accepted (not rejected with "not ready") in Finished state.
+    let rpc_response_collector = Arc::new(RwLock::new(vec![]));
+    let dummy_bitmask = BitVec::with_num_bits(4);
+    let rpc_req = new_signature_request_rpc(
+        999,
+        setup.addrs[1],
+        HashValue::zero(),
+        dummy_bitmask,
+        vec![],
+        rpc_response_collector.clone(),
+    );
+    let result = manager.process_peer_rpc_msg(rpc_req).await;
+    // Should succeed (handler spawned), not return "not ready" error.
+    assert!(result.is_ok());
+    let last_responses = std::mem::take(&mut *rpc_response_collector.write());
+    // Response is sent asynchronously by the spawned handler, so it may not
+    // be available immediately. The important check is that process_peer_rpc_msg
+    // didn't reject the request. The response collector may be empty at this
+    // point (handler still running) — that's fine.
+    // Verify no "not ready" error was sent synchronously.
+    for resp in &last_responses {
+        if let Err(e) = resp {
+            assert!(
+                !e.to_string().contains("not ready"),
+                "Signature request should be accepted in Finished state"
+            );
+        }
+    }
+}
+
+#[tokio::test]
+async fn test_signature_request_rejected_in_init_and_aggregation_states() {
+    let setup = ChunkyTestSetup::new_uniform(4);
+    let mut manager = create_test_manager(&setup);
+
+    let rpc_response_collector = Arc::new(RwLock::new(vec![]));
+    let dummy_bitmask = BitVec::with_num_bits(4);
+
+    // Init state — should be rejected with "not ready".
+    let rpc_req = new_signature_request_rpc(
+        999,
+        setup.addrs[1],
+        HashValue::zero(),
+        dummy_bitmask.clone(),
+        vec![],
+        rpc_response_collector.clone(),
+    );
+    let result = manager.process_peer_rpc_msg(rpc_req).await;
+    assert!(result.is_ok());
+    let last_responses = std::mem::take(&mut *rpc_response_collector.write());
+    assert_eq!(last_responses.len(), 1);
+    assert!(last_responses[0].is_err());
+    assert!(last_responses[0]
+        .as_ref()
+        .unwrap_err()
+        .to_string()
+        .contains("not ready"));
+
+    // AwaitSubtranscriptAggregation state — should also be rejected.
+    let event = ChunkyDKGStartEvent {
+        session_metadata: setup.session_metadata.clone(),
+        start_time_us: Duration::from_secs(1700000000).as_micros() as u64,
+    };
+    manager.process_dkg_start_event(event).await.unwrap();
+    assert_eq!(manager.state_name(), "AwaitSubtranscriptAggregation");
+
+    let rpc_req = new_signature_request_rpc(
+        999,
+        setup.addrs[1],
+        HashValue::zero(),
+        dummy_bitmask,
+        vec![],
+        rpc_response_collector.clone(),
+    );
+    let result = manager.process_peer_rpc_msg(rpc_req).await;
+    assert!(result.is_ok());
+    let last_responses = std::mem::take(&mut *rpc_response_collector.write());
+    assert_eq!(last_responses.len(), 1);
+    assert!(last_responses[0].is_err());
+    assert!(last_responses[0]
+        .as_ref()
+        .unwrap_err()
+        .to_string()
+        .contains("not ready"));
+}
+
+#[tokio::test]
+async fn test_signature_request_rate_limited_per_sender() {
+    let setup = ChunkyTestSetup::new_uniform(4);
+    let mut manager = create_test_manager(&setup);
+    advance_to_finished(&mut manager, &setup).await;
+
+    let rpc_response_collector = Arc::new(RwLock::new(vec![]));
+    let dummy_bitmask = BitVec::with_num_bits(4);
+
+    // First request from sender 1 — should be accepted and spawns a handler.
+    let rpc_req = new_signature_request_rpc(
+        999,
+        setup.addrs[1],
+        HashValue::zero(),
+        dummy_bitmask.clone(),
+        vec![],
+        rpc_response_collector.clone(),
+    );
+    manager.process_peer_rpc_msg(rpc_req).await.unwrap();
+
+    // Second request from the SAME sender with a DIFFERENT hash — should be
+    // rate-limited because the first handler is still running.
+    let rpc_req = new_signature_request_rpc(
+        999,
+        setup.addrs[1],
+        HashValue::from_u64(42),
+        dummy_bitmask.clone(),
+        vec![],
+        rpc_response_collector.clone(),
+    );
+    manager.process_peer_rpc_msg(rpc_req).await.unwrap();
+    let last_responses = std::mem::take(&mut *rpc_response_collector.write());
+    // The rate-limited response is sent synchronously.
+    let has_rate_limited = last_responses.iter().any(|r| {
+        r.as_ref()
+            .err()
+            .is_some_and(|e| e.to_string().contains("already in-flight"))
+    });
+    assert!(
+        has_rate_limited,
+        "Second concurrent request from same sender should be rate-limited"
+    );
+
+    // Request from a DIFFERENT sender should still be accepted.
+    let rpc_req = new_signature_request_rpc(
+        999,
+        setup.addrs[2],
+        HashValue::zero(),
+        dummy_bitmask,
+        vec![],
+        rpc_response_collector.clone(),
+    );
+    let result = manager.process_peer_rpc_msg(rpc_req).await;
+    assert!(result.is_ok());
+}
```

### dkg/src/chunky/missing_transcript_fetcher.rs
```diff
@@ -3,8 +3,8 @@
 
 use crate::{
     chunky::{
+        common::deserialize_chunky_transcript_and_verify,
         types::{ChunkyTranscriptWithHash, MissingTranscriptRequest},
-        validation::validate_chunky_transcript,
     },
     network::NetworkSender,
     DKGMessage,
@@ -191,14 +191,12 @@ impl TranscriptFetcher {
             ));
         }
 
-        let mut rng = rand::thread_rng();
-        validate_chunky_transcript(
+        deserialize_chunky_transcript_and_verify(
             dealer_addr,
             &transcript_response.transcript_bytes,
             &self.dkg_config,
             signing_pubkeys,
             &self.epoch_state,
-            &mut rng,
         )
     }
 }
```

### dkg/src/chunky/mod.rs
```diff
@@ -4,10 +4,10 @@
 pub use aptos_types::dkg::chunky_dkg::{DIGEST_KEY, PUBLIC_PARAMETERS};
 
 pub mod agg_subtrx_producer;
+pub mod common;
 pub mod dkg_manager;
 pub mod missing_transcript_fetcher;
 pub mod subtrx_cert_producer;
 #[cfg(test)]
 pub(crate) mod test_utils;
 pub mod types;
-pub mod validation;
```

### dkg/src/chunky/subtrx_cert_producer.rs
```diff
@@ -40,7 +40,7 @@ pub fn start_chunky_subtranscript_certification(
     let req = ChunkyDKGSubtranscriptSignatureRequest::new(
         epoch,
         aggregated_subtranscript.hash(),
-        aggregated_subtranscript.dealers.clone(),
+        aggregated_subtranscript.dealer_bitmask.clone(),
         dealer_transcript_hashes,
     );
     let validation_state = Arc::new(ChunkySubtranscriptCertificationState::new(
@@ -96,6 +96,7 @@ pub struct ChunkySubtranscriptCertificationState {
     sig_aggregator: Mutex<ChunkySubtranscriptSignatureAggregator>,
     epoch_state: Arc<EpochState>,
     aggregated_subtranscript: Arc<AggregatedSubtranscript>,
+    expected_subtranscript_hash: HashValue,
 }
 
 impl ChunkySubtranscriptCertificationState {
@@ -105,12 +106,14 @@ impl ChunkySubtranscriptCertificationState {
         epoch_state: Arc<EpochState>,
         aggregated_subtranscript: Arc<AggregatedSubtranscript>,
     ) -> Self {
+        let expected_subtranscript_hash = aggregated_subtranscript.hash();
         Self {
             start_time,
             my_addr,
             sig_aggregator: Mutex::new(ChunkySubtranscriptSignatureAggregator::default()),
             epoch_state,
             aggregated_subtranscript,
+            expected_subtranscript_hash,
         }
     }
 }
@@ -148,7 +151,7 @@ impl BroadcastStatus<DKGMessage> for Arc<ChunkySubtranscriptCertificationState>
             self.epoch_state.epoch,
         );
         ensure!(
-            subtranscript_hash == self.aggregated_subtranscript.hash(),
+            subtranscript_hash == self.expected_subtranscript_hash,
             "[ChunkyDKG] signature response hash does not match local aggregated subtranscript hash",
         );
 
@@ -338,6 +341,34 @@ mod tests {
         assert!(result.is_err());
     }
 
+    #[tokio::test]
+    async fn test_certification_rejects_wrong_epoch_signature() {
+        let setup = ChunkyTestSetup::new_uniform(4);
+        let agg_subtrx = setup.aggregate_subtranscripts(&[0, 1, 2]);
+        let state = make_cert_state(&setup, agg_subtrx);
+
+        // Sign a different AggregatedSubtranscript with a wrong epoch.
+        let mut wrong_epoch_agg = setup.aggregate_subtranscripts(&[0, 1, 2]);
+        wrong_epoch_agg.dealer_epoch = 998;
+        let stale_sig = setup.private_keys[0].sign(&wrong_epoch_agg).unwrap();
+        let stale_resp =
+            ChunkyDKGSubtranscriptSignatureResponse::new(998, wrong_epoch_agg.hash(), stale_sig);
+        // Epoch mismatch is caught in metadata checks.
+        let result = BroadcastStatus::add(&state, setup.addrs[0], stale_resp);
+        assert!(result.is_err());
+
+        // Even if the response claims the right epoch, the signature is over the wrong data
+        // (different epoch in AggregatedSubtranscript changes the hash).
+        let stale_sig2 = setup.private_keys[0].sign(&wrong_epoch_agg).unwrap();
+        let spoofed_resp = ChunkyDKGSubtranscriptSignatureResponse::new(
+            999,
+            state.aggregated_subtranscript().hash(),
+            stale_sig2,
+        );
+        let result = BroadcastStatus::add(&state, setup.addrs[0], spoofed_resp);
+        assert!(result.is_err());
+    }
+
     #[tokio::test]
     async fn test_certification_ignores_duplicate() {
         let setup = ChunkyTestSetup::new_uniform(4);
```

### dkg/src/chunky/test_utils.rs
```diff
@@ -2,11 +2,15 @@
 // Licensed pursuant to the Innovation-Enabling Source Code License, available at https://github.com/aptos-labs/aptos-core/blob/main/LICENSE
 
 use crate::{chunky::types::AggregatedSubtranscriptWithHashes, types::DKGMessage};
+use aptos_bitvec::BitVec;
 use aptos_crypto::{
     bls12381::{PrivateKey, PublicKey},
     HashValue, Uniform,
 };
-use aptos_dkg::pvss::{traits::transcript::HasAggregatableSubtranscript, Player};
+use aptos_dkg::pvss::{
+    traits::{transcript::HasAggregatableSubtranscript, Transcript},
+    Player,
+};
 use aptos_reliable_broadcast::RBNetworkSender;
 use aptos_types::{
     chain_id::ChainId,
@@ -100,9 +104,12 @@ impl ChunkyTestSetup {
             id: validator_index,
         };
 
-        let trx = self.dkg_config.deal(
+        let trx = ChunkyTranscript::deal(
+            &self.dkg_config.threshold_config,
+            &self.dkg_config.public_parameters,
             &self.private_keys[validator_index],
             &self.public_keys[validator_index],
+            &self.dkg_config.eks,
             &input_secret,
             &self.session_metadata,
             &dealer,
@@ -133,29 +140,18 @@ impl ChunkyTestSetup {
         let agg =
             Aggregatable::aggregate(&self.dkg_config.threshold_config, subtranscripts).unwrap();
 
-        let mut sorted_indices: Vec<usize> = indices.to_vec();
-        sorted_indices.sort();
-        // Map indices through address sort order to match production code behavior.
-        // Production code sorts contributors by AccountAddress, then maps to Player indices.
-        // We must do the same.
-        let mut contributor_addrs: Vec<AccountAddress> =
-            indices.iter().map(|&i| self.addrs[i]).collect();
-        contributor_addrs.sort();
-        let addr_to_index = self
-            .epoch_state
-            .verifier
-            .address_to_validator_index()
-            .clone();
-        let dealers: Vec<Player> = contributor_addrs
-            .into_iter()
-            .map(|addr| Player {
-                id: *addr_to_index.get(&addr).unwrap(),
-            })
-            .collect();
+        let addr_to_index = self.epoch_state.verifier.address_to_validator_index();
+        let num_validators = self.epoch_state.verifier.len();
+        let mut dealer_bitmask = BitVec::with_num_bits(num_validators as u16);
+        for &i in indices {
+            let idx = *addr_to_index.get(&self.addrs[i]).unwrap();
+            dealer_bitmask.set(idx as u16);
+        }
 
         AggregatedSubtranscript {
+            dealer_epoch: 999,
             subtranscript: agg,
-            dealers,
+            dealer_bitmask,
         }
     }
 
@@ -178,30 +174,26 @@ impl ChunkyTestSetup {
         let agg =
             Aggregatable::aggregate(&self.dkg_config.threshold_config, subtranscripts).unwrap();
 
-        let mut contributor_addrs: Vec<AccountAddress> =
-            indices.iter().map(|&i| self.addrs[i]).collect();
-        contributor_addrs.sort();
-        let addr_to_index = self
-            .epoch_state
-            .verifier
-            .address_to_validator_index()
-            .clone();
-        let dealers: Vec<Player> = contributor_addrs
-            .iter()
-            .map(|addr| Player {
-                id: *addr_to_index.get(addr).unwrap(),
-            })
-            .collect();
+        let addr_to_index = self.epoch_state.verifier.address_to_validator_index();
+        let ordered_addrs = self.epoch_state.verifier.get_ordered_account_addresses();
+        let num_validators = self.epoch_state.verifier.len();
+        let mut dealer_bitmask = BitVec::with_num_bits(num_validators as u16);
+        for &i in indices {
+            let idx = *addr_to_index.get(&self.addrs[i]).unwrap();
+            dealer_bitmask.set(idx as u16);
+        }
 
         // Build a map from addr to transcript for hash lookup
         let addr_to_transcript: HashMap<AccountAddress, &ChunkyTranscript> = indices
             .iter()
             .map(|&i| (self.addrs[i], &transcripts[i]))
             .collect();
 
-        let dealer_transcript_hashes: Vec<HashValue> = contributor_addrs
-            .iter()
-            .map(|addr| {
+        // Per-dealer hashes ordered by set-bit position (ascending validator index).
+        let dealer_transcript_hashes: Vec<HashValue> = dealer_bitmask
+            .iter_ones()
+            .map(|idx| {
+                let addr = &ordered_addrs[idx];
                 let transcript = addr_to_transcript.get(addr).unwrap();
                 let bytes = bcs::to_bytes(*transcript).unwrap();
                 HashValue::sha3_256_of(&bytes)
@@ -210,8 +202,9 @@ impl ChunkyTestSetup {
 
         AggregatedSubtranscriptWithHashes {
             aggregated_subtranscript: AggregatedSubtranscript {
+                dealer_epoch: 999,
                 subtranscript: agg,
-                dealers,
+                dealer_bitmask,
             },
             dealer_transcript_hashes,
         }
```
