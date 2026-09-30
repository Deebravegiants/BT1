# [?] apollo_consensus_orchestrator: remove some panics from the validate proposal flow (#8048)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/sequencer
Published: 2025-07-24
Source: https://github.com/starkware-libs/sequencer/commit/b22673d099f008d65e2b89e1cc1ed968a1926f3e
Type: security-commit

## Details
apollo_consensus_orchestrator: remove some panics from the validate proposal flow (#8048)

Failures here can simply result in the proposal being treated as invalid.

## Patch
### crates/apollo_consensus_orchestrator/src/validate_proposal.rs
```diff
@@ -13,6 +13,7 @@ use apollo_batcher_types::batcher_types::{
     ValidateBlockInput,
 };
 use apollo_batcher_types::communication::{BatcherClient, BatcherClientError};
+use apollo_batcher_types::errors::BatcherError;
 use apollo_class_manager_types::transaction_converter::TransactionConverterTrait;
 use apollo_consensus::types::ProposalCommitment;
 use apollo_l1_gas_price_types::errors::{EthToStrkOracleClientError, L1GasPriceClientError};
@@ -427,13 +428,20 @@ async fn handle_proposal_part(
                 proposal_id,
                 content: SendProposalContent::Finish(final_n_executed_txs_nonopt),
             };
-            let response = batcher.send_proposal_content(input).await.unwrap_or_else(|e| {
-                panic!("Failed to send Fin to batcher: {proposal_id:?}. {e:?}")
-            });
+            let response = match batcher.send_proposal_content(input).await {
+                Ok(response) => response,
+                Err(e) => {
+                    return HandledProposalPart::Failed(format!(
+                        "Failed to send Fin to batcher: {e:?}"
+                    ));
+                }
+            };
             let response_id = match response.response {
                 ProposalStatus::Finished(id) => id,
                 ProposalStatus::InvalidProposal(err) => return HandledProposalPart::Invalid(err),
-                status => panic!("Unexpected status: for {proposal_id:?}, {status:?}"),
+                status => {
+                    unreachable!("Unexpected batcher status for fin: {status:?}");
+                }
             };
             let batcher_block_id = BlockHash(response_id.state_diff_commitment.0.0);
 
@@ -479,13 +487,20 @@ async fn handle_proposal_part(
             content.push(txs.clone());
             let input =
                 SendProposalContentInput { proposal_id, content: SendProposalContent::Txs(txs) };
-            let response = batcher.send_proposal_content(input).await.unwrap_or_else(|e| {
-                panic!("Failed to send proposal content to batcher: {proposal_id:?}. {e:?}")
-            });
+            let response = match batcher.send_proposal_content(input).await {
+                Ok(response) => response,
+                Err(e) => {
+                    return HandledProposalPart::Failed(format!(
+                        "Failed to send transactions to batcher: {e:?}"
+                    ));
+                }
+            };
             match response.response {
                 ProposalStatus::Processing => HandledProposalPart::Continue,
                 ProposalStatus::InvalidProposal(err) => HandledProposalPart::Invalid(err),
-                status => panic!("Unexpected status: for {proposal_id:?}, {status:?}"),
+                status => {
+                    unreachable!("Unexpected batcher status for transactions: {status:?}");
+                }
             }
         }
         Some(ProposalPart::ExecutedTransactionCount(executed_txs_count)) => {
@@ -510,10 +525,36 @@ async fn handle_proposal_part(
     }
 }
 
+// TODO(alonl, matan): consider making the retry logic part of the client interface.
 async fn batcher_abort_proposal(batcher: &dyn BatcherClient, proposal_id: ProposalId) {
     let input = SendProposalContentInput { proposal_id, content: SendProposalContent::Abort };
-    batcher
-        .send_proposal_content(input)
-        .await
-        .unwrap_or_else(|e| panic!("Failed to send Abort to batcher: {proposal_id:?}. {e:?}"));
+
+    const MAX_CLIENT_RETRIES: usize = 10;
+    let mut client_attempts = 0;
+
+    loop {
+        match batcher.send_proposal_content(input.clone()).await {
+            Ok(_) => return, // Success - abort sent successfully
+
+            Err(BatcherClientError::BatcherError(BatcherError::ProposalAborted)) => {
+                warn!("Proposal {proposal_id:?} was already aborted by batcher");
+                return;
+            }
+
+            Err(BatcherClientError::BatcherError(e)) => {
+                panic!("Batcher failed to abort proposal {proposal_id:?}: {e:?}");
+            }
+
+            Err(BatcherClientError::ClientError(e)) => {
+                client_attempts += 1;
+                if client_attempts >= MAX_CLIENT_RETRIES {
+                    panic!(
+                        "Failed to send abort to batcher after {MAX_CLIENT_RETRIES} attempts: \
+                         {e:?}"
+                    );
+                }
+                // Continue loop for retry
+            }
+        }
+    }
 }
```
