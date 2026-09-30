# [?] fix: avoid light-client panic on frozen block body metadata

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2026-06-02
Source: https://github.com/nervosnetwork/ckb/commit/8c80639c49f568a3a57f47f6e52cac98144c87fe
Type: security-commit

## Details
fix: avoid light-client panic on frozen block body metadata

When the freezer prunes historical block body data from RocksDB,
get_block_uncles() and get_block_extension() return None for frozen
blocks.  The light-client proof handlers called .expect() on these,
causing a panic on valid remote requests.

Use snapshot.get_block() instead, which already checks freezer.number()
and reads from the append-only freezer files when the block has been
frozen.  The BlockView reconstructed from freezer data carries the same
calc_uncles_hash() and extension() values.

## Patch
### util/light-client-protocol-server/src/components/get_blocks_proof.rs
```diff
@@ -79,19 +79,17 @@ impl<'a> GetBlocksProofProcess<'a> {
         let mut extensions = Vec::with_capacity(found.len());
 
         for block_hash in found {
-            let header = snapshot
-                .get_block_header(&block_hash)
-                .expect("header should be in store");
-            positions.push(leaf_index_to_pos(header.number()));
-            block_headers.push(header.data());
-
-            let uncles = snapshot
-                .get_block_uncles(&block_hash)
-                .expect("block uncles must be stored");
-            let extension = snapshot.get_block_extension(&block_hash);
-
-            uncles_hash.push(uncles.data().calc_uncles_hash());
-            extensions.push(packed::BytesOpt::new_builder().set(extension).build());
+            let block = snapshot
+                .get_block(&block_hash)
+                .expect("block should be in store");
+            positions.push(leaf_index_to_pos(block.number()));
+            block_headers.push(block.header().data());
+            uncles_hash.push(block.calc_uncles_hash());
+            extensions.push(
+                packed::BytesOpt::new_builder()
+                    .set(block.extension())
+                    .build(),
+            );
         }
 
         let proved_items = (
```

### util/light-client-protocol-server/src/components/get_transactions_proof.rs
```diff
@@ -125,13 +125,12 @@ impl<'a> GetTransactionsProofProcess<'a> {
             positions.push(leaf_index_to_pos(block.number()));
             filtered_blocks.push(filtered_block);
 
-            let uncles = snapshot
-                .get_block_uncles(&block_hash)
-                .expect("block uncles must be stored");
-            let extension = snapshot.get_block_extension(&block_hash);
-
-            uncles_hash.push(uncles.data().calc_uncles_hash());
-            extensions.push(packed::BytesOpt::new_builder().set(extension).build());
+            uncles_hash.push(block.calc_uncles_hash());
+            extensions.push(
+                packed::BytesOpt::new_builder()
+                    .set(block.extension())
+                    .build(),
+            );
         }
 
         let proved_items = (
```
