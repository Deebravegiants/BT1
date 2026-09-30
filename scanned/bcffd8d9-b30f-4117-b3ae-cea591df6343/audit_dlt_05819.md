# [?] fix(spice): avoid panic when re-endorsing a chunk certified on another fork (#15909)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2026-06-15
Source: https://github.com/near/nearcore/commit/fd672206c21f26269a9bf1bdcc0efdeb4cc4170d
Type: security-commit

## Details
fix(spice): avoid panic when re-endorsing a chunk certified on another fork (#15909)

`record_block_core_statements` panicked with "for each endorsement we
should save corresponding uncertified execution result" when a block's
endorsement core statements re-crossed the endorsement threshold for a
chunk whose execution result was already certified.

Certification is recorded in the fork-agnostic `execution_results`
column (keyed only by the endorsed chunk), while `uncertified_chunks` is
ancestry-relative, so a producer building on a branch that lacks the
certifying block legitimately re-emits the endorsement core statements.
If the node had certified that chunk via a `ChunkExecutionResult` core
statement on another fork (which never populates
`uncertified_execution_results`), re-deriving the endorsed state
demanded an uncertified result that was never stored, and the
`.expect()` panicked.

Skip the chunk when its result is already present in
`execution_results`: there is nothing to materialize. Adds a regression
test that certifies a chunk on one fork and re-emits a sub-threshold
endorsement on a sibling fork.

## Patch
### chain/chain/src/spice/core_writer_actor.rs
```diff
@@ -485,6 +485,15 @@ impl SpiceCoreWriterActor {
             if in_block_execution_results.contains(chunk_id) {
                 continue;
             }
+            // Already certified on another fork: `execution_results` is keyed only by the chunk,
+            // while `uncertified_chunks` is ancestry-relative, so a fork lacking the certifying
+            // block re-emits these endorsements; that certification saved no uncertified result.
+            if self
+                .get_execution_result_from_store(&chunk_id.block_hash, chunk_id.shard_id)
+                .is_some()
+            {
+                continue;
+            }
 
             let endorsement_block = self.chain_store.get_block(&chunk_id.block_hash)?;
             let chunk_validator_assignments = self.epoch_manager.get_chunk_validator_assignments(
```

### chain/chain/src/spice/tests/core_writer_actor.rs
```diff
@@ -404,6 +404,51 @@ fn test_handle_processed_block_for_block_with_final_endorsement_and_no_execution
     assert!(execution_results.contains_key(&chunk_header.shard_id()));
 }
 
+#[test]
+#[cfg_attr(not(feature = "protocol_feature_spice"), ignore)]
+fn test_handle_processed_block_with_endorsements_for_chunk_certified_on_another_fork() {
+    let (mut chain, core_writer_actor) = setup();
+    let genesis = chain.genesis_block();
+    let block = build_block(&mut chain, &genesis, vec![]);
+    process_block(&mut chain, block.clone());
+    let chunks = block.chunks();
+    let chunk_header = chunks.iter_raw().next().unwrap();
+
+    let all_validators = test_validators();
+    let execution_result = test_execution_result_for_chunk(&chunk_header);
+    let endorsement = |validator: &str| {
+        endorsement_into_core_statement(test_chunk_endorsement(validator, &block, chunk_header))
+    };
+    let (early_endorsers, late_endorsers) = all_validators.split_at(all_validators.len() / 2);
+
+    // Sub-threshold endorsements land on chain first, without certifying the chunk.
+    let early_endorsements = early_endorsers.iter().map(|v| endorsement(v)).collect_vec();
+    let accumulating = build_block(&mut chain, &block, early_endorsements.clone());
+    process_block(&mut chain, accumulating.clone());
+    core_writer_actor.handle_processed_block(*accumulating.hash()).unwrap();
+
+    // The certifying fork adds the remaining endorsements and the result. Certifying via a core
+    // statement stores the result without populating uncertified_execution_results.
+    let mut certifying_statements = late_endorsers.iter().map(|v| endorsement(v)).collect_vec();
+    certifying_statements.push(SpiceCoreStatement::ChunkExecutionResult {
+        chunk_id: SpiceChunkId { block_hash: *block.hash(), shard_id: chunk_header.shard_id() },
+        execution_result: execution_result.clone(),
+    });
+    let certifying_fork = build_block(&mut chain, &accumulating, certifying_statements);
+    process_block(&mut chain, certifying_fork.clone());
+    core_writer_actor.handle_processed_block(*certifying_fork.hash()).unwrap();
+
+    // A sibling fork lacking the certifying block re-emits its still-uncertified endorsements. The
+    // globally stored endorsements re-cross the threshold and must not need the uncertified result.
+    let endorsing_fork = build_block(&mut chain, &block, early_endorsements);
+    process_block(&mut chain, endorsing_fork.clone());
+    core_writer_actor.handle_processed_block(*endorsing_fork.hash()).unwrap();
+
+    let execution_results =
+        core_writer_actor.core_reader.get_execution_results_by_shard_id(block.header()).unwrap();
+    assert_eq!(execution_results.get(&chunk_header.shard_id()), Some(&Arc::new(execution_result)));
+}
+
 #[test]
 #[cfg_attr(not(feature = "protocol_feature_spice"), ignore)]
 fn test_handle_processed_block_for_block_with_execution_results() {
```
