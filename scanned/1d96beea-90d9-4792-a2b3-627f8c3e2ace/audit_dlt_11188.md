# [?] apollo_batcher,apollo_consensus_orchestrator: reject duplicate proposal txs instead of panicking (#14840)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/sequencer
Published: 2026-07-21
Source: https://github.com/starkware-libs/sequencer/commit/64a743eb9c6da7caa0841e299d5ba239ce203b35
Type: security-commit

## Details
apollo_batcher,apollo_consensus_orchestrator: reject duplicate proposal txs instead of panicking (#14840)

## Patch
### crates/apollo_batcher/src/block_builder.rs
```diff
@@ -116,6 +116,8 @@ pub enum FailOnErrorCause {
     TransactionFailed(BlockifierTransactionExecutorError),
     #[error("L1 Handler transaction validation failed: {0}")]
     L1HandlerTransactionValidationFailed(TransactionProviderError),
+    #[error("Duplicate transaction hash in proposal: {0}")]
+    DuplicateTransaction(TransactionHash),
 }
 
 enum AddTxsToExecutorResult {
@@ -635,11 +637,21 @@ async fn collect_execution_results_and_stream_txs(
         // Insert the tx_hash into the appropriate collection if it's an L1_Handler transaction.
         if let InternalConsensusTransaction::L1Handler(_) = input_tx {
             let is_new_entry = execution_data.consumed_l1_handler_tx_hashes.insert(tx_hash);
-            // Even though this doesn't get past the set insertion, this indicates a major, possibly
-            // reorg-producing bug, either in some batcher cache or the l1 provider.
+            // Unlike the duplicate account/RPC hashes handled below, a duplicate L1 handler hash is
+            // never valid input: it signals a batcher-cache or l1-provider fault, possibly
+            // reorg-producing. Keep it a hard invariant.
             assert!(is_new_entry, "Duplicate L1 handler transaction hash: {tx_hash}.");
         }
 
+        // Check for duplicates in both the executed and rejected collections.
+        if execution_data.execution_infos_and_signatures.contains_key(&tx_hash)
+            || execution_data.rejected_tx_hashes.contains(&tx_hash)
+        {
+            return Err(BlockBuilderError::FailOnError(FailOnErrorCause::DuplicateTransaction(
+                tx_hash,
+            )));
+        }
+
         match result {
             Ok((tx_execution_info, state_maps)) => {
                 if let Some(ref revert_error) = tx_execution_info.revert_error {
@@ -650,12 +662,10 @@ async fn collect_execution_results_and_stream_txs(
                         revert_error,
                     );
                 }
-                let (tx_index, duplicate_tx_hash) =
-                    execution_data.execution_infos_and_signatures.insert_full(
-                        tx_hash,
-                        (tx_execution_info, input_tx.tx_signature_for_commitment()),
-                    );
-                assert_eq!(duplicate_tx_hash, None, "Duplicate transaction: {tx_hash}.");
+                let (tx_index, _) = execution_data.execution_infos_and_signatures.insert_full(
+                    tx_hash,
+                    (tx_execution_info, input_tx.tx_signature_for_commitment()),
+                );
 
                 if let Some(block_number) = proof_facts_block_number(input_tx) {
                     execution_data.proof_facts_block_numbers.insert(tx_hash, block_number);
@@ -703,8 +713,7 @@ async fn collect_execution_results_and_stream_txs(
                     tx_hash,
                     err.log_compatible_to_string()
                 );
-                let is_new_entry = execution_data.rejected_tx_hashes.insert(tx_hash);
-                assert!(is_new_entry, "Duplicate rejected transaction hash: {tx_hash}.");
+                execution_data.rejected_tx_hashes.insert(tx_hash);
             }
         }
     }
```

### crates/apollo_batcher/src/block_builder_test.rs
```diff
@@ -1305,3 +1305,110 @@ async fn proof_facts_block_numbers_collected_from_snos_invokes() {
         IndexMap::from([(tx_hash!(0), proof_block_number)]),
     );
 }
+
+#[tokio::test]
+async fn validate_block_rejects_duplicate_rejected_account_tx() {
+    let mut input_txs = test_txs(0..2);
+    input_txs.push(input_txs[0].clone());
+
+    let mut helper = ExpectationHelper::new();
+    helper.expect_successful_get_new_results(0);
+    helper.expect_add_txs_to_block(&input_txs);
+    helper.expect_get_new_results_with_results(
+        input_txs
+            .iter()
+            .map(|_| {
+                Err(TransactionExecutorError::StateError(StateError::OutOfRangeContractAddress))
+            })
+            .collect(),
+    );
+    helper.mock_transaction_executor.expect_close_block().times(0);
+    helper.mock_transaction_executor.expect_abort_block().times(1).return_once(|| ());
+
+    let mock_tx_provider = mock_tx_provider_limited_calls(vec![input_txs]);
+    let (_abort_sender, abort_receiver) = tokio::sync::oneshot::channel();
+    let result = run_build_block(
+        helper.mock_transaction_executor,
+        mock_tx_provider,
+        None,
+        true,
+        abort_receiver,
+        BLOCK_GENERATION_DEADLINE_SECS,
+        DEFAULT_IDLE_TIMEOUT_MS,
+    )
+    .await;
+
+    assert_matches!(
+        result,
+        Err(BlockBuilderError::FailOnError(FailOnErrorCause::DuplicateTransaction(tx_hash)))
+        if tx_hash == tx_hash!(0)
+    );
+}
+
+#[tokio::test]
+async fn validate_block_rejects_duplicate_successful_account_tx() {
+    let mut input_txs = test_txs(0..2);
+    input_txs.push(input_txs[0].clone());
+
+    let mut helper = ExpectationHelper::new();
+    helper.expect_successful_get_new_results(0);
+    helper.expect_add_txs_to_block(&input_txs);
+    helper.expect_successful_get_new_results(input_txs.len());
+    helper.mock_transaction_executor.expect_close_block().times(0);
+    helper.mock_transaction_executor.expect_abort_block().times(1).return_once(|| ());
+
+    let mock_tx_provider = mock_tx_provider_limited_calls(vec![input_txs]);
+    let (_abort_sender, abort_receiver) = tokio::sync::oneshot::channel();
+    let result = run_build_block(
+        helper.mock_transaction_executor,
+        mock_tx_provider,
+        None,
+        true,
+        abort_receiver,
+        BLOCK_GENERATION_DEADLINE_SECS,
+        DEFAULT_IDLE_TIMEOUT_MS,
+    )
+    .await;
+
+    assert_matches!(
+        result,
+        Err(BlockBuilderError::FailOnError(FailOnErrorCause::DuplicateTransaction(tx_hash)))
+        if tx_hash == tx_hash!(0)
+    );
+}
+
+#[tokio::test]
+async fn validate_block_rejects_duplicate_account_tx_executed_then_rejected() {
+    let mut input_txs = test_txs(0..2);
+    input_txs.push(input_txs[0].clone());
+
+    let mut helper = ExpectationHelper::new();
+    helper.expect_successful_get_new_results(0);
+    helper.expect_add_txs_to_block(&input_txs);
+    helper.expect_get_new_results_with_results(vec![
+        Ok((execution_info(), StateMaps::default())),
+        Ok((execution_info(), StateMaps::default())),
+        Err(TransactionExecutorError::StateError(StateError::OutOfRangeContractAddress)),
+    ]);
+    helper.mock_transaction_executor.expect_close_block().times(0);
+    helper.mock_transaction_executor.expect_abort_block().times(1).return_once(|| ());
+
+    let mock_tx_provider = mock_tx_provider_limited_calls(vec![input_txs]);
+    let (_abort_sender, abort_receiver) = tokio::sync::oneshot::channel();
+    let result = run_build_block(
+        helper.mock_transaction_executor,
+        mock_tx_provider,
+        None,
+        true,
+        abort_receiver,
+        BLOCK_GENERATION_DEADLINE_SECS,
+        DEFAULT_IDLE_TIMEOUT_MS,
+    )
+    .await;
+
+    assert_matches!(
+        result,
+        Err(BlockBuilderError::FailOnError(FailOnErrorCause::DuplicateTransaction(tx_hash)))
+        if tx_hash == tx_hash!(0)
+    );
+}
```

### crates/apollo_consensus_orchestrator/src/validate_proposal.rs
```diff
@@ -26,6 +26,7 @@ use apollo_transaction_converter::{TransactionConverterTrait, VerifyAndStoreProo
 use apollo_versioned_constants::VersionedConstants;
 use futures::channel::mpsc;
 use futures::StreamExt;
+use indexmap::IndexSet;
 use starknet_api::block::{BlockNumber, GasPrice, StarknetVersion};
 use starknet_api::consensus_transaction::InternalConsensusTransaction;
 use starknet_api::data_availability::L1DataAvailabilityMode;
@@ -143,6 +144,7 @@ pub(crate) async fn validate_proposal(
 ) -> ValidateProposalResult<ProposalCommitment> {
     let mut content = Vec::new();
     let mut verify_and_store_proof_tasks: Vec<VerifyAndStoreProofTask> = Vec::new();
+    let mut seen_tx_hashes: IndexSet<TransactionHash> = IndexSet::new();
     let now = args.deps.clock.now();
 
     let Some(deadline) = now.checked_add_signed(chrono::TimeDelta::from_std(args.timeout).unwrap())
@@ -199,6 +201,7 @@ pub(crate) async fn validate_proposal(
                     args.deps.batcher.as_ref(),
                     proposal_part.clone(),
                     &mut content,
+                    &mut seen_tx_hashes,
                     &mut verify_and_store_proof_tasks,
                     args.deps.transaction_converter.clone(),
                     &deadline_params,
@@ -492,6 +495,7 @@ async fn handle_proposal_part(
     batcher: &dyn BatcherClient,
     proposal_part: Option<ProposalPart>,
     content: &mut Vec<Vec<InternalConsensusTransaction>>,
+    seen_tx_hashes: &mut IndexSet<TransactionHash>,
     verify_and_store_proof_tasks: &mut Vec<VerifyAndStoreProofTask>,
     transaction_converter: Arc<dyn TransactionConverterTrait>,
     deadline_params: &ProposalDeadlineParams,
@@ -630,6 +634,15 @@ async fn handle_proposal_part(
                 txs.iter().map(|tx| tx.tx_hash()).collect::<Vec<TransactionHash>>()
             );
 
+            for tx in &txs {
+                let tx_hash = tx.tx_hash();
+                if !seen_tx_hashes.insert(tx_hash) {
+                    return HandledProposalPart::Failed(format!(
+                        "Duplicate transaction hash in proposal: {tx_hash}."
+                    ));
+                }
+            }
+
             content.push(txs.clone());
             let input = SendTxsForProposalInput { proposal_id, txs };
             let response = match batcher.send_txs_for_proposal(input).await {
```

### crates/apollo_consensus_orchestrator/src/validate_proposal_test.rs
```diff
@@ -247,6 +247,36 @@ async fn fin_with_inflated_executed_tx_count_is_rejected() {
     assert_matches!(res, Err(ValidateProposalError::ProposalPartFailed(_, _)));
 }
 
+#[tokio::test]
+async fn duplicate_transaction_hash_in_proposal_is_rejected_before_batcher() {
+    let (mut proposal_args, mut content_sender) = create_proposal_validate_arguments();
+    proposal_args.deps.batcher.expect_validate_block().times(1).returning(|_| Ok(()));
+    proposal_args
+        .deps
+        .batcher
+        .expect_start_height()
+        .withf(|input| input.height == BlockNumber(0))
+        .return_const(Ok(()));
+    proposal_args.deps.batcher.expect_send_txs_for_proposal().times(0);
+    proposal_args.deps.batcher.expect_finish_proposal().times(0);
+    proposal_args.deps.batcher.expect_abort_proposal().times(1).returning(|_| Ok(()));
+
+    let duplicate_tx = TX_BATCH[0].clone();
+    content_sender
+        .send(ProposalPart::Transactions(TransactionBatch {
+            transactions: vec![duplicate_tx.clone(), duplicate_tx],
+        }))
+        .await
+        .unwrap();
+
+    let res = validate_proposal(proposal_args.into()).await;
+    assert_matches!(
+        res,
+        Err(ValidateProposalError::ProposalPartFailed(reason, _))
+        if reason.contains("Duplicate transaction hash")
+    );
+}
+
 #[tokio::test]
 async fn interrupt_proposal() {
     let (mut proposal_args, _content_sender) = create_proposal_validate_arguments();
```
