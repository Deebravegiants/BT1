# [?] Fix race condition in ChunkEndorsementTracker (#11452)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2024-06-04
Source: https://github.com/near/nearcore/commit/041c32c760d335bbb7c70ab881a741bb7acaaccb
Type: security-commit

## Details
Fix race condition in ChunkEndorsementTracker (#11452)

Fixes: https://github.com/near/nearcore/issues/11445

In the new version all operations are done by
`ChunkEndorsementTrackerInner` which has `&mut self` on all methods,
which prevents most races. Apart from that when adding a pending
endorsement we check whether the header for this chunk has already been
seen and if so we treat this endorsement as non-pending.

## Patch
### chain/client/src/stateless_validation/chunk_endorsement_tracker.rs
```diff
@@ -1,7 +1,7 @@
-use near_cache::SyncLruCache;
+use lru::LruCache;
 use near_chain::ChainStoreAccess;
 use std::collections::HashMap;
-use std::sync::Arc;
+use std::sync::{Arc, Mutex};
 
 use near_chain_primitives::Error;
 use near_epoch_manager::EpochManagerAdapter;
@@ -33,15 +33,21 @@ impl ChunkEndorsementsState {
 
 /// Module to track chunk endorsements received from chunk validators.
 pub struct ChunkEndorsementTracker {
+    epoch_manager: Arc<dyn EpochManagerAdapter>,
+    inner: Mutex<ChunkEndorsementTrackerInner>,
+}
+
+struct ChunkEndorsementTrackerInner {
     epoch_manager: Arc<dyn EpochManagerAdapter>,
     /// We store the validated chunk endorsements received from chunk validators
     /// This is keyed on chunk_hash and account_id of validator to avoid duplicates.
     /// Chunk endorsements would later be used as a part of block production.
-    chunk_endorsements: SyncLruCache<ChunkHash, HashMap<AccountId, ChunkEndorsement>>,
+    chunk_endorsements:
+        LruCache<ChunkHash, (ShardChunkHeader, HashMap<AccountId, ChunkEndorsement>)>,
     /// We store chunk endorsements to be processed later because we did not have
     /// chunks ready at the time we received that endorsements from validators.
     /// This is keyed on chunk_hash and account_id of validator to avoid duplicates.
-    pending_chunk_endorsements: SyncLruCache<ChunkHash, HashMap<AccountId, ChunkEndorsement>>,
+    pending_chunk_endorsements: LruCache<ChunkHash, HashMap<AccountId, ChunkEndorsement>>,
 }
 
 impl Client {
@@ -69,38 +75,28 @@ impl Client {
 impl ChunkEndorsementTracker {
     pub fn new(epoch_manager: Arc<dyn EpochManagerAdapter>) -> Self {
         Self {
-            epoch_manager,
-            chunk_endorsements: SyncLruCache::new(NUM_CHUNKS_IN_CHUNK_ENDORSEMENTS_CACHE),
-            // We can use a different cache size if needed, it does not have to be the same as for `chunk_endorsements`.
-            pending_chunk_endorsements: SyncLruCache::new(NUM_CHUNKS_IN_CHUNK_ENDORSEMENTS_CACHE),
+            epoch_manager: epoch_manager.clone(),
+            inner: Mutex::new(ChunkEndorsementTrackerInner {
+                epoch_manager,
+                chunk_endorsements: LruCache::new(NUM_CHUNKS_IN_CHUNK_ENDORSEMENTS_CACHE),
+                // We can use a different cache size if needed, it does not have to be the same as for `chunk_endorsements`.
+                pending_chunk_endorsements: LruCache::new(NUM_CHUNKS_IN_CHUNK_ENDORSEMENTS_CACHE),
+            }),
         }
     }
 
     /// Process pending endorsements for the given chunk header.
     /// It removes these endorsements from the `pending_chunk_endorsements` cache.
     pub fn process_pending_endorsements(&self, chunk_header: &ShardChunkHeader) {
-        let chunk_hash = &chunk_header.chunk_hash();
-        let chunk_endorsements = {
-            let mut guard = self.pending_chunk_endorsements.lock();
-            guard.pop(chunk_hash)
-        };
-        let Some(chunk_endorsements) = chunk_endorsements else {
-            return;
-        };
-        tracing::debug!(target: "client", ?chunk_hash, "Processing pending chunk endorsements.");
-        for endorsement in chunk_endorsements.values() {
-            if let Err(error) = self.process_chunk_endorsement(chunk_header, endorsement.clone()) {
-                tracing::debug!(target: "client", ?endorsement, ?error, "Error processing pending chunk endorsement");
-            }
-        }
+        self.inner.lock().unwrap().process_pending_endorsements(chunk_header);
     }
 
     /// Add the chunk endorsement to a cache of pending chunk endorsements (if not yet there).
     pub(crate) fn add_chunk_endorsement_to_pending_cache(
         &self,
         endorsement: ChunkEndorsement,
     ) -> Result<(), Error> {
-        self.process_chunk_endorsement_impl(endorsement, None)
+        self.inner.lock().unwrap().process_chunk_endorsement_impl(endorsement, None, false)
     }
 
     /// Function to process an incoming chunk endorsement from chunk validators.
@@ -112,65 +108,117 @@ impl ChunkEndorsementTracker {
         endorsement: ChunkEndorsement,
     ) -> Result<(), Error> {
         let _span = tracing::debug_span!(target: "client", "process_chunk_endorsement", chunk_hash=?chunk_header.chunk_hash()).entered();
-        self.process_chunk_endorsement_impl(endorsement, Some(chunk_header))
+
+        // Validate the endorsement before locking the mutex to improve performance.
+        if !self.epoch_manager.verify_chunk_endorsement(&chunk_header, &endorsement)? {
+            tracing::error!(target: "client", ?endorsement, "Invalid chunk endorsement.");
+            return Err(Error::InvalidChunkEndorsement);
+        }
+        self.inner.lock().unwrap().process_chunk_endorsement_impl(
+            endorsement,
+            Some(chunk_header),
+            true,
+        )
+    }
+
+    /// Called by block producer.
+    /// Returns ChunkEndorsementsState::Endorsed if node has enough signed stake for the chunk
+    /// represented by chunk_header.
+    /// Signatures have the same order as ordered_chunk_validators, thus ready to be included in a block as is.
+    /// Returns ChunkEndorsementsState::NotEnoughStake if chunk doesn't have enough stake.
+    /// For older protocol version, we return ChunkEndorsementsState::Endorsed with an empty array of
+    /// chunk endorsements.
+    pub fn compute_chunk_endorsements(
+        &self,
+        chunk_header: &ShardChunkHeader,
+    ) -> Result<ChunkEndorsementsState, Error> {
+        self.inner.lock().unwrap().compute_chunk_endorsements_impl(chunk_header)
+    }
+}
+
+impl ChunkEndorsementTrackerInner {
+    /// Process pending endorsements for the given chunk header.
+    /// It removes these endorsements from the `pending_chunk_endorsements` cache.
+    pub fn process_pending_endorsements(&mut self, chunk_header: &ShardChunkHeader) {
+        let chunk_hash = &chunk_header.chunk_hash();
+        let chunk_endorsements = self.pending_chunk_endorsements.pop(chunk_hash);
+        let Some(chunk_endorsements) = chunk_endorsements else {
+            return;
+        };
+        tracing::debug!(target: "client", ?chunk_hash, "Processing pending chunk endorsements.");
+        for endorsement in chunk_endorsements.values() {
+            if let Err(error) =
+                self.process_chunk_endorsement_impl(endorsement.clone(), Some(chunk_header), false)
+            {
+                tracing::debug!(target: "client", ?endorsement, ?error, "Error processing pending chunk endorsement");
+            }
+        }
     }
 
     /// If the chunk header is available, we will verify the chunk endorsement and then store it in a cache.
     /// Otherwise, we store the endorsement in a separate cache of endorsements to be processed when the chunk is ready.
     fn process_chunk_endorsement_impl(
-        &self,
+        &mut self,
         endorsement: ChunkEndorsement,
         chunk_header: Option<&ShardChunkHeader>,
+        already_validated: bool,
     ) -> Result<(), Error> {
         let chunk_hash = endorsement.chunk_hash();
         let account_id = &endorsement.account_id;
 
-        let endorsement_cache = if chunk_header.is_some() {
-            &self.chunk_endorsements
-        } else {
-            &self.pending_chunk_endorsements
-        };
+        let existing_entry = self.chunk_endorsements.peek(chunk_hash);
 
         // If we have already processed this chunk endorsement, return early.
-        if endorsement_cache
-            .get(chunk_hash)
-            .is_some_and(|existing_endorsements| existing_endorsements.contains_key(account_id))
-        {
+        if existing_entry.is_some_and(|(_, existing_endorsements)| {
+            existing_endorsements.contains_key(account_id)
+        }) {
             tracing::debug!(target: "client", ?endorsement, "Already received chunk endorsement.");
             return Ok(());
         }
 
-        if let Some(chunk_header) = chunk_header {
-            if !self.epoch_manager.verify_chunk_endorsement(&chunk_header, &endorsement)? {
-                tracing::error!(target: "client", ?endorsement, "Invalid chunk endorsement.");
-                return Err(Error::InvalidChunkEndorsement);
-            }
-        }
-
         // If we are the current block producer, we store the chunk endorsement for each chunk which
         // would later be used during block production to check whether to include the chunk or not.
         // TODO(stateless_validation): It's possible for a malicious validator to send endorsements
         // for 100 unique chunks thus pushing out current valid endorsements from our cache.
         // Maybe add check to ensure we don't accept endorsements from chunks already included in some block?
         // Maybe add check to ensure we don't accept endorsements from chunks that have too old height_created?
         tracing::debug!(target: "client", ?endorsement, "Received and saved chunk endorsement.");
-        let mut guard = endorsement_cache.lock();
-        guard.get_or_insert(chunk_hash.clone(), || HashMap::new());
-        let chunk_endorsements = guard.get_mut(chunk_hash).unwrap();
-        chunk_endorsements.insert(account_id.clone(), endorsement);
+
+        // The header might be available in the endorsement cache, even if it isn't provided.
+        // In such case it should be treated as a non-pending endorsement.
+        let header = chunk_header.or_else(|| existing_entry.map(|(header, _)| header));
+
+        if let Some(chunk_header) = header {
+            if !already_validated
+                && !self.epoch_manager.verify_chunk_endorsement(&chunk_header, &endorsement)?
+            {
+                tracing::error!(target: "client", ?endorsement, "Invalid chunk endorsement.");
+                return Err(Error::InvalidChunkEndorsement);
+            }
+
+            if self.chunk_endorsements.peek(chunk_hash).is_none() {
+                self.chunk_endorsements
+                    .put(chunk_hash.clone(), (chunk_header.clone(), HashMap::new()));
+            }
+            self.chunk_endorsements
+                .get_mut(chunk_hash)
+                .unwrap()
+                .1
+                .insert(account_id.clone(), endorsement);
+        } else {
+            // Chunk header is not available, store the endorsement in the pending cache.
+            self.pending_chunk_endorsements.get_or_insert(chunk_hash.clone(), || HashMap::new());
+            self.pending_chunk_endorsements
+                .get_mut(chunk_hash)
+                .unwrap()
+                .insert(account_id.clone(), endorsement);
+        }
 
         Ok(())
     }
 
-    /// Called by block producer.
-    /// Returns ChunkEndorsementsState::Endorsed if node has enough signed stake for the chunk
-    /// represented by chunk_header.
-    /// Signatures have the same order as ordered_chunk_validators, thus ready to be included in a block as is.
-    /// Returns ChunkEndorsementsState::NotEnoughStake if chunk doesn't have enough stake.
-    /// For older protocol version, we return ChunkEndorsementsState::Endorsed with an empty array of
-    /// chunk endorsements.
-    pub fn compute_chunk_endorsements(
-        &self,
+    pub fn compute_chunk_endorsements_impl(
+        &mut self,
         chunk_header: &ShardChunkHeader,
     ) -> Result<ChunkEndorsementsState, Error> {
         let epoch_id =
@@ -191,7 +239,8 @@ impl ChunkEndorsementTracker {
         // We can safely rely on the following details
         //    1. The chunk endorsements are from valid chunk_validator for this chunk.
         //    2. The chunk endorsements signatures are valid.
-        let Some(chunk_endorsements) = self.chunk_endorsements.get(&chunk_header.chunk_hash())
+        let Some((_header, chunk_endorsements)) =
+            self.chunk_endorsements.get(&chunk_header.chunk_hash())
         else {
             // Early return if no chunk_endorsements found in our cache.
             return Ok(ChunkEndorsementsState::NotEnoughStake(None));
```
