# [?] fix: overflow in horizon computation (#15332)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2026-03-06
Source: https://github.com/near/nearcore/commit/49a520b36c5463ae626ea4376c71c3c48b00acfc
Type: security-commit

## Details
fix: overflow in horizon computation (#15332)

- rewrote height_within_front_horizon and height_within_rear_horizon in
chain/chunks/src/chunk_cache.rs to avoid integer overflow when
largest_seen_height or height is near u64::MAX.
- added test_height_within_horizon_no_overflow covering normal ranges,
largest_seen_height = 0, and largest_seen_height = u64::MAX.

## Patch
### chain/chunks/src/chunk_cache.rs
```diff
@@ -256,12 +256,12 @@ impl EncodedChunksCache {
     }
 
     pub fn height_within_front_horizon(&self, height: BlockHeight) -> bool {
-        height >= self.largest_seen_height && height <= self.largest_seen_height + MAX_HEIGHTS_AHEAD
+        height >= self.largest_seen_height && height - self.largest_seen_height <= MAX_HEIGHTS_AHEAD
     }
 
     pub fn height_within_rear_horizon(&self, height: BlockHeight) -> bool {
-        height + self.height_horizon >= self.largest_seen_height
-            && height <= self.largest_seen_height
+        height <= self.largest_seen_height
+            && self.largest_seen_height - height <= self.height_horizon
     }
 
     pub fn height_within_horizon(&self, height: BlockHeight) -> bool {
@@ -337,7 +337,7 @@ impl EncodedChunksCache {
 mod tests {
     use std::collections::{HashMap, HashSet};
 
-    use super::DEFAULT_CHUNKS_CACHE_HEIGHT_HORIZON;
+    use super::{DEFAULT_CHUNKS_CACHE_HEIGHT_HORIZON, MAX_HEIGHTS_AHEAD};
     use near_crypto::KeyType;
     use near_primitives::hash::CryptoHash;
     use near_primitives::sharding::{ShardChunkHeader, ShardChunkHeaderV2};
@@ -393,6 +393,39 @@ mod tests {
         assert_eq!(cache.get_incomplete_chunks(&CryptoHash::default()), None);
     }
 
+    #[test]
+    fn test_height_within_horizon_no_overflow() {
+        let horizon = DEFAULT_CHUNKS_CACHE_HEIGHT_HORIZON;
+        let mut cache = EncodedChunksCache::new(horizon);
+
+        // Normal range: largest_seen_height well above the rear horizon.
+        let lsh = horizon * 128 + 1;
+        cache.largest_seen_height = lsh;
+        assert!(cache.height_within_horizon(lsh)); // exactly at largest_seen
+        assert!(cache.height_within_horizon(lsh + MAX_HEIGHTS_AHEAD)); // at front boundary
+        assert!(!cache.height_within_horizon(lsh + MAX_HEIGHTS_AHEAD + 1)); // just past front boundary
+        assert!(cache.height_within_horizon(lsh - horizon)); // at rear boundary
+        assert!(!cache.height_within_horizon(lsh - horizon - 1)); // just past rear boundary
+        // height=u64::MAX or 0 with normal largest_seen_height should not panic.
+        assert!(!cache.height_within_horizon(0));
+        assert!(!cache.height_within_horizon(u64::MAX));
+
+        // Edge case: largest_seen_height = 0.
+        let lsh = 0;
+        cache.largest_seen_height = lsh;
+        assert!(cache.height_within_horizon(lsh)); // exactly at largest_seen
+        assert!(cache.height_within_horizon(MAX_HEIGHTS_AHEAD)); // at front boundary
+        assert!(!cache.height_within_horizon(MAX_HEIGHTS_AHEAD + 1)); // just past front boundary
+        assert!(!cache.height_within_horizon(u64::MAX)); // should not crash
+
+        // Edge case: largest_seen_height = u64::MAX.
+        let lsh = u64::MAX;
+        cache.largest_seen_height = lsh;
+        assert!(cache.height_within_horizon(u64::MAX)); // exactly at largest_seen
+        assert!(cache.height_within_horizon(lsh - horizon)); // rear boundary
+        assert!(!cache.height_within_horizon(lsh - horizon - 1)); // just past rear boundary
+    }
+
     #[test]
     fn test_cache_removal() {
         let mut cache = EncodedChunksCache::new(DEFAULT_CHUNKS_CACHE_HEIGHT_HORIZON);
```
