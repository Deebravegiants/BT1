# [?] fix - prevent race condition in reconstructing witness (#13794)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2025-06-27
Source: https://github.com/near/nearcore/commit/d4c7a74f9c555bf48219538c25beb7087036eb59
Type: security-commit

## Details
fix - prevent race condition in reconstructing witness (#13794)

We must check `processed_witnesses` under lock, to avoid some race
condition that can lead to process twice the same SW.

Note that the race conditions happen only if SW parts distribution is
changed in a way that multiple parts are delivered by multiple nodes at
very low latencies.

## Patch
### chain/client/src/stateless_validation/partial_witness/partial_witness_tracker.rs
```diff
@@ -42,7 +42,7 @@ const WITNESS_PARTS_CACHE_SIZE: usize = 5;
 /// Number of entries to keep in LRU cache of the processed state witnesses
 /// We only store small amount of data (ChunkProductionKey) per entry there,
 /// so we don't have to worry much about memory usage here.
-const PROCESSED_WITNESSES_CACHE_SIZE: usize = 200;
+const PROCESSED_WITNESSES_CACHE_SIZE: usize = 50;
 
 type DecodePartialWitnessResult = std::io::Result<EncodedChunkStateWitness>;
 
@@ -324,6 +324,27 @@ impl CacheEntry {
     }
 }
 
+/// Per-shard state tracking for partial witness processing.
+struct ShardWitnessTracker {
+    /// Cache of witness parts being assembled for this shard.
+    parts_cache: LruCache<ChunkProductionKey, CacheEntry>,
+    /// Track processed witnesses to avoid duplicate processing for this shard.
+    processed_witnesses: SyncLruCache<ChunkProductionKey, ()>,
+}
+
+impl ShardWitnessTracker {
+    fn new() -> Self {
+        Self {
+            parts_cache: LruCache::new(NonZeroUsize::new(WITNESS_PARTS_CACHE_SIZE).unwrap()),
+            processed_witnesses: SyncLruCache::new(PROCESSED_WITNESSES_CACHE_SIZE),
+        }
+    }
+
+    fn total_size(&self) -> usize {
+        self.parts_cache.iter().map(|(_, entry)| entry.total_size()).sum()
+    }
+}
+
 /// Track the Reed Solomon erasure encoded parts of the `EncodedChunkStateWitness`. These are created
 /// by the chunk producer and distributed to validators. Note that we do not need all the parts of to
 /// recreate the full state witness.
@@ -332,13 +353,9 @@ pub struct PartialEncodedStateWitnessTracker {
     client_sender: ClientSenderForPartialWitness,
     /// Epoch manager to get the set of chunk validators
     epoch_manager: Arc<dyn EpochManagerAdapter>,
-    /// Keeps track of state witness parts received from chunk producers.
+    /// Per-shard tracking of witness parts and processed witnesses.
     /// Each shard is tracked independently.
-    parts_cache: Mutex<HashMap<ShardId, Arc<Mutex<LruCache<ChunkProductionKey, CacheEntry>>>>>,
-    /// Keeps track of the already decoded witnesses. This is needed
-    /// to protect chunk validator from processing the same witness multiple
-    /// times.
-    processed_witnesses: SyncLruCache<ChunkProductionKey, ()>,
+    shard_trackers: Mutex<HashMap<ShardId, Arc<Mutex<ShardWitnessTracker>>>>,
     /// Reed Solomon encoder for decoding state witness parts.
     encoders: Mutex<ReedSolomonEncoderCache>,
 }
@@ -351,8 +368,7 @@ impl PartialEncodedStateWitnessTracker {
         Self {
             client_sender,
             epoch_manager,
-            parts_cache: Mutex::new(HashMap::new()),
-            processed_witnesses: SyncLruCache::new(PROCESSED_WITNESSES_CACHE_SIZE),
+            shard_trackers: Mutex::new(HashMap::new()),
             encoders: Mutex::new(ReedSolomonEncoderCache::new(WITNESS_RATIO_DATA_PARTS)),
         }
     }
@@ -394,45 +410,54 @@ impl PartialEncodedStateWitnessTracker {
         create_if_not_exists: bool,
         update: CacheUpdate,
     ) -> Result<(), Error> {
-        if self.processed_witnesses.contains(&key) {
+        let shard_tracker_mutex = {
+            let mut map = self.shard_trackers.lock();
+            Arc::clone(
+                map.entry(key.shard_id)
+                    .or_insert_with(|| Arc::new(Mutex::new(ShardWitnessTracker::new()))),
+            )
+        };
+        let mut shard_tracker = shard_tracker_mutex.lock();
+
+        // Check if this witness was already processed.
+        if shard_tracker.processed_witnesses.contains(&key) {
             tracing::debug!(
                 target: "client",
                 ?key,
-                "Received data for the already processed witness"
+                "Received data for already processed witness"
             );
             return Ok(());
         }
 
-        let parts_cache_by_shard_mutex = {
-            let mut map = self.parts_cache.lock();
-            Arc::clone(map.entry(key.shard_id).or_insert_with(|| {
-                Arc::new(Mutex::new(LruCache::new(
-                    NonZeroUsize::new(WITNESS_PARTS_CACHE_SIZE).unwrap(),
-                )))
-            }))
-        };
-        let mut parts_cache_by_shard = parts_cache_by_shard_mutex.lock();
-        if create_if_not_exists {
-            Self::maybe_insert_new_entry_in_parts_cache(&mut parts_cache_by_shard, &key);
-        }
-        let Some(entry) = parts_cache_by_shard.get_mut(&key) else {
-            return Ok(());
+        let (entry_update_result, entry_created_at) = {
+            if create_if_not_exists {
+                Self::maybe_insert_new_entry_in_parts_cache(&mut shard_tracker.parts_cache, &key);
+            }
+            let Some(entry) = shard_tracker.parts_cache.get_mut(&key) else {
+                return Ok(());
+            };
+
+            if let Some((decode_result, accessed_contracts)) = entry.update(update) {
+                let entry_created_at = entry.created_at;
+                shard_tracker.processed_witnesses.push(key.clone(), ());
+                shard_tracker.parts_cache.pop(&key);
+                (Some((decode_result, accessed_contracts)), entry_created_at)
+            } else {
+                (None, entry.created_at)
+            }
         };
 
         let total_size: usize = if let Some((decode_result, accessed_contracts)) =
-            entry.update(update)
+            entry_update_result
         {
-            self.processed_witnesses.push(key.clone(), ());
-
             // Record the time taken from receiving first part to decoding partial witness.
-            let time_to_last_part = Instant::now().signed_duration_since(entry.created_at);
+            let time_to_last_part = Instant::now().signed_duration_since(entry_created_at);
             metrics::PARTIAL_WITNESS_TIME_TO_LAST_PART
                 .with_label_values(&[key.shard_id.to_string().as_str()])
                 .observe(time_to_last_part.as_seconds_f64());
 
-            parts_cache_by_shard.pop(&key);
-            let total_size = parts_cache_by_shard.iter().map(|(_, entry)| entry.total_size()).sum();
-            drop(parts_cache_by_shard);
+            let total_size = shard_tracker.total_size();
+            drop(shard_tracker);
 
             let encoded_witness = match decode_result {
                 Ok(encoded_chunk_state_witness) => encoded_chunk_state_witness,
@@ -492,7 +517,7 @@ impl PartialEncodedStateWitnessTracker {
 
             total_size
         } else {
-            parts_cache_by_shard.iter().map(|(_, entry)| entry.total_size()).sum()
+            shard_tracker.total_size()
         };
         metrics::PARTIAL_WITNESS_CACHE_SIZE
             .with_label_values(&[key.shard_id.to_string().as_str()])
```
