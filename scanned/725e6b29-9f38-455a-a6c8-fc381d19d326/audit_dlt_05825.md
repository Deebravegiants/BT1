# [?] fix: spice: Do not crash when accessing debug info. (#14454)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2025-10-16
Source: https://github.com/near/nearcore/commit/f1d30b5353b01dd56da11d3a6193ca0fb31eb2ab
Type: security-commit

## Details
fix: spice: Do not crash when accessing debug info. (#14454)

In spice prev_state_root isn't part of chunks and we have debug_assert
false when accessing it (which is best to keep in place to catch any
unexpected and significant access points that need fixing).

## Patch
### chain/client/src/debug.rs
```diff
@@ -362,6 +362,10 @@ impl ClientActorInner {
                     .iter()
                     .enumerate()
                     .map(|(shard_index, chunk)| {
+                        // TODO(spice): chunks in spice no longer contain prev state root.
+                        if cfg!(feature = "protocol_feature_spice") {
+                            return (0, 0);
+                        }
                         let shard_id = shard_layout.get_shard_id(shard_index).unwrap();
                         let state_root_node = self.client.runtime_adapter.get_state_root_node(
                             shard_id,
```

### core/primitives/src/views.rs
```diff
@@ -1108,7 +1108,11 @@ impl From<ShardChunkHeader> for ChunkHeaderView {
             chunk_hash: hash,
             prev_block_hash: *inner.prev_block_hash(),
             outcome_root: *inner.prev_outcome_root(),
-            prev_state_root: *inner.prev_state_root(),
+            prev_state_root: if cfg!(feature = "protocol_feature_spice") {
+                CryptoHash::default()
+            } else {
+                *inner.prev_state_root()
+            },
             encoded_merkle_root: *inner.encoded_merkle_root(),
             encoded_length: inner.encoded_length(),
             height_created: inner.height_created(),
```
