# [?] Merge branch 'develop' into fix/clarity-cli-panic

## Summary
Severity: Unknown
Chain: Stacks
Component: stacks-network/stacks-core
Published: 2026-03-25
Source: https://github.com/stacks-network/stacks-core/commit/43a6fa42caf00c1bfd81539a0006c62a76536157
Type: security-commit

## Details
Merge branch 'develop' into fix/clarity-cli-panic

## Patch
### changelog.d/flaky-signer-test.fixed
```diff
@@ -0,0 +1 @@
+Fixed flakiness in `signer_waits_for_validation_before_signing` by waiting for state machine updates to prevent the signer from rejecting immediately.
\ No newline at end of file
```

### changelog.d/tenure-start-position-check.fixed
```diff
@@ -0,0 +1 @@
+Fixed logical operator in tenure-start block validation to correctly reject blocks where either the coinbase or tenure-change transaction is in the wrong position, not only when both are wrong
```

### stacks-node/src/tests/signer/v0/signers_wait_for_validation.rs
```diff
@@ -22,10 +22,12 @@ use tracing_subscriber::layer::SubscriberExt;
 use tracing_subscriber::util::SubscriberInitExt;
 use tracing_subscriber::{fmt, EnvFilter};
 
+use crate::nakamoto_node::miner::TEST_BROADCAST_PROPOSAL_STALL;
 use crate::tests::nakamoto_integrations::wait_for;
 use crate::tests::signer::v0::{
     get_stackerdb_signer_messages, wait_for_block_pre_commits_from_signers,
-    wait_for_block_pushed_by_miner_key, MultipleMinerTest,
+    wait_for_block_pushed_by_miner_key, wait_for_state_machine_update_by_miner_tenure_id,
+    MultipleMinerTest,
 };
 
 #[test]
@@ -136,9 +138,30 @@ fn signer_waits_for_validation_before_signing() {
     TEST_VALIDATE_STALL.set(vec![Some(node_2_auth)]);
 
     info!("------------------------- Mine Block N+1 with Stalled Validation -------------------------");
+    // Stall the miner's block proposal broadcast so that we can wait for
+    // state machine updates to propagate between the two nodes' stackerdbs
+    // before the proposal reaches signers. Without this, the signer on
+    // miner 2 may reject the proposal with NoSignerConsensus because it
+    // hasn't yet received state machine updates from the other signers.
+    TEST_BROADCAST_PROPOSAL_STALL.set(vec![miner_pk_1.clone()]);
+
     // Mine a new tenure which will issue a block proposal to all signers for its tenure change.
     miners.signer_test.mine_bitcoin_block();
 
+    // Wait for signers to broadcast state machine updates for the new tenure.
+    // This ensures that by the time we unstall the proposal, the signer on
+    // miner 2 will have received enough updates to establish global state.
+    let chain_info = miners.get_peer_info();
+    wait_for_state_machine_update_by_miner_tenure_id(
+        30,
+        &chain_info.pox_consensus,
+        &miners.signer_test.signer_addresses_versions(),
+    )
+    .expect("Timed out waiting for state machine updates from signers");
+
+    // Now let the proposal through
+    TEST_BROADCAST_PROPOSAL_STALL.set(vec![]);
+
     // The 4 signers on miner 1 should have validated and sent pre-commits
     // The 1 signer on miner 2 should be waiting for validation and should NOT have issued a signature
     let block =
```

### stacks-signer/changelog.d/fix-signer-return.fixed
```diff
@@ -0,0 +1 @@
+Fixed an issue in the signer where it would return early if it detected a message from an unrecognized signer.
\ No newline at end of file
```

### stacks-signer/src/v0/signer.rs
```diff
@@ -530,7 +530,7 @@ impl Signer {
                             "signer_address" => %signer_address,
                             "message" => ?message,
                         );
-                        return;
+                        continue;
                     }
                     match message {
                         SignerMessage::BlockResponse(block_response) => {
```

### stackslib/src/chainstate/nakamoto/mod.rs
```diff
@@ -1342,7 +1342,7 @@ impl NakamotoBlock {
         // have both a coinbase and a tenure-change
         let coinbase_idx = 1;
         let tc_idx = 0;
-        if coinbase_position != Some(coinbase_idx) && tenure_change_position != Some(tc_idx) {
+        if coinbase_position != Some(coinbase_idx) || tenure_change_position != Some(tc_idx) {
             // invalid -- expect exactly one sortition-induced tenure change and exactly one coinbase expected,
             // and the tenure change must be the first transaction and the coinbase must be the second transaction
             warn!("Invalid block -- coinbase and/or tenure change txs are in the wrong position -- ({coinbase_positions:?}, {tenure_change_positions:?}) != [{coinbase_idx}], [{tc_idx}]";
```
