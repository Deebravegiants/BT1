# [?] fix(spice): execution results race condition (#14953)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2026-02-03
Source: https://github.com/near/nearcore/commit/9c9c28f4dba386601276e207ac5bc64926ecfffc
Type: security-commit

## Details
fix(spice): execution results race condition (#14953)

I think there is a race condition with spice execution results:

`postprocess_ready_block`:
1. `record_uncertified_chunks_for_block` updates
`DBCol::uncertified_chunks` to reflect
which chunks were certified by this block's `ChunkExecutionResult` core
statements.
2. `check_orphans` runs immediately after - if an orphan child block
exists, it calls
`start_process_block_impl`, which calls
`get_last_certified_execution_results_for_next_block`.

That function needs the execution results for the last certified block.
It checks two places:
the store (`DBCol::execution_results`) and the current block's core
statements. But execution
results are only written to the store asynchronously. So neither source
has the data, and the lookup panics.

So I changed `get_last_certified_execution_results_for_next_block` to
look at parent blocks for the necessary results.
In most cases, this should be a short chain.

## Patch
### chain/chain/src/spice_core.rs
```diff
@@ -379,20 +379,13 @@ impl SpiceCoreReader {
         block_header: &BlockHeader,
         core_statements_for_next_block: &[SpiceCoreStatement],
     ) -> Result<BlockExecutionResults, Error> {
-        let new_execution_results: HashMap<_, _> = core_statements_for_next_block
-            .iter()
-            .filter_map(|core_statement| match core_statement {
-                SpiceCoreStatement::ChunkExecutionResult { execution_result, chunk_id } => {
-                    Some((chunk_id, execution_result))
-                }
-                _ => None,
-            })
-            .collect();
+        let newly_certified_chunks: HashSet<&SpiceChunkId> =
+            iter_execution_results(core_statements_for_next_block).map(|(id, _)| id).collect();
 
         let mut uncertified_chunks =
             get_uncertified_chunks(&self.chain_store, block_header.hash())?;
         uncertified_chunks
-            .retain(|chunk_info| !new_execution_results.contains_key(&chunk_info.chunk_id));
+            .retain(|chunk_info| !newly_certified_chunks.contains(&chunk_info.chunk_id));
         let oldest_uncertified_block_header =
             find_oldest_uncertified_block_header(&self.chain_store, uncertified_chunks)?;
         let last_certified_block_header =
@@ -403,25 +396,66 @@ impl SpiceCoreReader {
                 block_header
             };
 
-        let mut execution_results =
-            self.get_execution_results_by_shard_id(last_certified_block_header)?;
+        if last_certified_block_header.is_genesis() {
+            return Ok(BlockExecutionResults(
+                self.get_execution_results_by_shard_id(last_certified_block_header)?,
+            ));
+        }
 
-        for shard_id in self.epoch_manager.shard_ids(block_header.epoch_id())? {
-            if execution_results.contains_key(&shard_id) {
+        let last_certified_hash = *last_certified_block_header.hash();
+        let num_shards =
+            self.epoch_manager.shard_ids(last_certified_block_header.epoch_id())?.len();
+        let mut execution_results: HashMap<ShardId, Arc<ChunkExecutionResult>> = HashMap::new();
+        for (chunk_id, result) in iter_execution_results(core_statements_for_next_block) {
+            if chunk_id.block_hash != last_certified_hash {
                 continue;
             }
-            let execution_result = new_execution_results
-            .get(&SpiceChunkId { block_hash: *last_certified_block_header.hash(), shard_id })
-            .expect(
-                "for certified block we should have execution either in store or core statements",
-            );
-            execution_results.insert(shard_id, Arc::new((*execution_result).clone()));
+            execution_results.entry(chunk_id.shard_id).or_insert_with(|| Arc::new(result.clone()));
         }
 
+        // Walk backwards from block_header, collecting execution results from
+        // each block's core statements. We can't depend on reading from
+        // DBCol::execution_results, which SpiceCoreWriterActor writes
+        // asynchronously. So, during orphan processing, the results we need
+        // here may not be persisted to that column yet.
+        let mut current_hash = *block_header.hash();
+        while execution_results.len() < num_shards && current_hash != last_certified_hash {
+            let block = self.chain_store.get_block(&current_hash)?;
+            for (chunk_id, result) in iter_execution_results(block.spice_core_statements()) {
+                if chunk_id.block_hash != last_certified_hash {
+                    continue;
+                }
+                execution_results
+                    .entry(chunk_id.shard_id)
+                    .or_insert_with(|| Arc::new(result.clone()));
+            }
+            current_hash = *block.header().prev_hash();
+        }
+
+        assert_eq!(
+            execution_results.len(),
+            num_shards,
+            "should have found all shard's execution results for last certified block"
+        );
         Ok(BlockExecutionResults(execution_results))
     }
 }
 
+fn iter_execution_results(
+    core_statements: &[SpiceCoreStatement],
+) -> impl Iterator<Item = (&SpiceChunkId, &ChunkExecutionResult)> {
+    // TODO(spice): Consider making a newtype wrapper for list of
+    // SpiceCoreStatements. Would also be good if it worked with any iterators
+    // generally (i.e. generics implementing IntoIterator trait). so we can
+    // write: block.spice_core_statements().iter_execution_results()
+    core_statements.iter().filter_map(|s| match s {
+        SpiceCoreStatement::ChunkExecutionResult { chunk_id, execution_result } => {
+            Some((chunk_id, execution_result))
+        }
+        _ => None,
+    })
+}
+
 fn get_uncertified_chunks(
     chain_store: &ChainStoreAdapter,
     block_hash: &CryptoHash,
@@ -446,16 +480,7 @@ fn get_uncertified_chunks(
 }
 
 fn get_block_execution_results(block: &Block) -> HashMap<&SpiceChunkId, &ChunkExecutionResult> {
-    block
-        .spice_core_statements()
-        .iter()
-        .filter_map(|core_statement| match core_statement {
-            SpiceCoreStatement::ChunkExecutionResult { execution_result, chunk_id } => {
-                Some((chunk_id, execution_result))
-            }
-            _ => None,
-        })
-        .collect()
+    iter_execution_results(block.spice_core_statements()).collect()
 }
 
 fn get_block_endorsements(
```

### chain/chain/src/tests/spice_core.rs
```diff
@@ -1179,6 +1179,56 @@ fn test_get_last_certified_execution_results_for_next_block_with_certification_s
     assert_eq!(block_execution_results, execution_results);
 }
 
+// This test verifies `get_last_certified_execution_results_for_next_block` works without
+// `SpiceCoreWriterActor` having processed the blocks. This matters during orphan processing,
+// when multiple blocks can be processed in quick succession and the core writer (which
+// runs asynchronously) may not have caught up yet.
+#[test]
+#[cfg_attr(not(feature = "protocol_feature_spice"), ignore)]
+fn test_get_last_certified_execution_results_without_core_writer_execution_result_in_core() {
+    let (mut chain, core_reader) = setup();
+    let genesis = chain.genesis_block();
+    let block = build_block(&mut chain, &genesis, vec![]);
+    process_block(&mut chain, block.clone());
+
+    let core_statements = block_certification_core_statements(&block);
+    let next_block = build_block(&mut chain, &block, core_statements);
+    process_block(&mut chain, next_block.clone());
+
+    assert!(core_reader.get_execution_results_by_shard_id(block.header()).unwrap().is_empty());
+    let execution_results = core_reader
+        .get_last_certified_execution_results_for_next_block(next_block.header(), &[])
+        .unwrap();
+    let block_execution_results = block_execution_results(&block);
+    assert_eq!(block_execution_results, execution_results);
+}
+
+#[test]
+#[cfg_attr(not(feature = "protocol_feature_spice"), ignore)]
+fn test_get_last_certified_execution_results_without_core_writer_old_block_certified() {
+    let (mut chain, core_reader) = setup();
+    let genesis = chain.genesis_block();
+    let block = build_block(&mut chain, &genesis, vec![]);
+    process_block(&mut chain, block.clone());
+
+    let core_statements = block_certification_core_statements(&block);
+    let mut last_block = build_block(&mut chain, &block, core_statements);
+    process_block(&mut chain, last_block.clone());
+
+    for _ in 0..3 {
+        let new_block = build_block(&chain, &last_block, vec![]);
+        process_block(&mut chain, new_block.clone());
+        last_block = new_block;
+    }
+
+    assert!(core_reader.get_execution_results_by_shard_id(block.header()).unwrap().is_empty());
+    let execution_results = core_reader
+        .get_last_certified_execution_results_for_next_block(last_block.header(), &[])
+        .unwrap();
+    let block_execution_results = block_execution_results(&block);
+    assert_eq!(block_execution_results, execution_results);
+}
+
 fn block_execution_results(block: &Block) -> BlockExecutionResults {
     let mut results = HashMap::new();
     for chunk in block.chunks().iter_raw() {
```
