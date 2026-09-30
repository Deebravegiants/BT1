# [?] Fix race condition: wait for the tip to advance before continuing after wait_for_block_pushed

## Summary
Severity: Unknown
Chain: Stacks
Component: stacks-network/stacks-core
Published: 2026-03-12
Source: https://github.com/stacks-network/stacks-core/commit/3aa237a81e2ef39804296607a7b8612d8c5a42d5
Type: security-commit

## Details
Fix race condition: wait for the tip to advance before continuing after wait_for_block_pushed

Signed-off-by: Jacinta Ferrant <236437600+jacinta-stacks@users.noreply.github.com>

## Patch
### stacks-node/src/tests/signer/v0/capitulate_parent_tenure_view.rs
```diff
@@ -133,12 +133,13 @@ fn deadlock_50_50_split_capitulates_to_node_tip() {
     .expect("Timed out waiting for N to be mined and processed");
 
     // Ensure that the block was accepted globally so the stacks tip has advanced to N
-    let block_n =
-        wait_for_block_pushed_by_miner_key(30, info_before.stacks_tip_height + 1, &miner_pk)
-            .expect("Timed out waiting for block N to be mined");
+    let _block_n =
+        wait_for_block_pushed_and_tip(30, info_before.stacks_tip_height + 1, &miner_pk, || {
+            signer_test.get_peer_info().stacks_tip
+        })
+        .expect("Timed out waiting for block N to be mined");
 
     let info_after = signer_test.get_peer_info();
-    assert_eq!(info_after.stacks_tip, block_n.header.block_hash());
     assert_eq!(
         info_after.stacks_tip_height,
         info_before.stacks_tip_height + 1
@@ -400,12 +401,13 @@ fn minority_signers_capitulate_to_supermajority_consensus() {
     .expect("Timed out waiting for N to be mined and processed");
 
     // Ensure that the block was accepted globally so the stacks tip has advanced to N
-    let block_n =
-        wait_for_block_pushed_by_miner_key(30, info_before.stacks_tip_height + 1, &miner_pk)
-            .expect("Timed out waiting for block N to be mined");
+    let _block_n =
+        wait_for_block_pushed_and_tip(30, info_before.stacks_tip_height + 1, &miner_pk, || {
+            signer_test.get_peer_info().stacks_tip
+        })
+        .expect("Timed out waiting for block N to be mined");
 
     let info_after = signer_test.get_peer_info();
-    assert_eq!(info_after.stacks_tip, block_n.header.block_hash());
     assert_eq!(
         info_after.stacks_tip_height,
         info_before.stacks_tip_height + 1
```

### stacks-node/src/tests/signer/v0/late_block_proposal.rs
```diff
@@ -31,7 +31,7 @@ use super::SignerTest;
 use crate::tests::nakamoto_integrations::wait_for;
 use crate::tests::neon_integrations::{get_chain_info, submit_tx, test_observer};
 use crate::tests::signer::v0::{
-    get_stackerdb_signer_messages, wait_for_block_proposal, wait_for_block_pushed_by_miner_key,
+    get_stackerdb_signer_messages, wait_for_block_proposal, wait_for_block_pushed_and_tip,
 };
 
 #[tag(bitcoind)]
@@ -108,15 +108,10 @@ fn signer_rejects_proposal_after_block_pushed() {
         wait_for_block_proposal(30, info_before.stacks_tip_height + 1, &miner_pk)
             .expect("Timed out waiting for block N+1 to be proposed");
     let signer_signature_hash = block_n_proposal.block.header.signer_signature_hash();
-    let _ = wait_for_block_pushed_by_miner_key(30, info_before.stacks_tip_height + 1, &miner_pk)
-        .expect("Failed to get BlockPushed for block N");
-    info!("------------------------- Advance Chain to Include Block N -------------------------");
-    // Shouldn't have to wait long for the chain to advance
-    wait_for(10, || {
-        let info_after = get_chain_info(&signer_test.running_nodes.conf);
-        Ok(info_after.stacks_tip_height >= info_before.stacks_tip_height + 1)
+    let _ = wait_for_block_pushed_and_tip(30, info_before.stacks_tip_height + 1, &miner_pk, || {
+        get_chain_info(&signer_test.running_nodes.conf).stacks_tip
     })
-    .expect("Chain did not advance to block N+1");
+    .expect("Failed to get BlockPushed for block N");
 
     info!("------------------------- Verify Signer 1 did NOT respond to the Block Proposal -------------------------");
     let messages = get_stackerdb_signer_messages();
```

### stacks-node/src/tests/signer/v0/mod.rs
```diff
@@ -1357,9 +1357,30 @@ pub fn wait_for_block_pushed_by_miner_key(
         }
         Ok(false)
     })?;
+
     block.ok_or_else(|| "Failed to find block pushed".to_string())
 }
 
+/// Waits for a block to be pushed by the specified miner, then waits for
+/// the node's tip to advance to that block. This prevents race conditions
+/// where subsequent calls read a stale `stacks_tip_height` because the
+/// coordinator hasn't yet processed the pushed block.
+///
+/// `get_tip` should return the current stacks tip hash (e.g. from
+/// `get_peer_info().stacks_tip` or `get_chain_info().stacks_tip`).
+pub fn wait_for_block_pushed_and_tip(
+    timeout_secs: u64,
+    expected_height: u64,
+    expected_miner: &StacksPublicKey,
+    get_tip: impl Fn() -> BlockHeaderHash,
+) -> Result<NakamotoBlock, String> {
+    let block = wait_for_block_pushed_by_miner_key(timeout_secs, expected_height, expected_miner)?;
+    let block_hash = block.header.block_hash();
+    wait_for(timeout_secs, || Ok(get_tip() == block_hash))
+        .map_err(|e| format!("Tip did not advance to pushed block: {e}"))?;
+    Ok(block)
+}
+
 /// Waits for all of the provided signers to send a pre-commit for a block
 /// with the provided signer signature hash
 pub fn wait_for_block_pre_commits_from_signers(
@@ -4058,14 +4079,10 @@ fn miner_recovers_when_broadcast_block_delay_across_tenures_occurs() {
     info!("Submitted tx {tx} in to mine block N");
     sender_nonce += 1;
     let block_n =
-        wait_for_block_pushed_by_miner_key(30, info_before.stacks_tip_height + 1, &miner_pk)
-            .expect("Timed out waiting for block N to be mined");
-
-    wait_for(30, || {
-        let info = signer_test.get_peer_info();
-        Ok(info.stacks_tip == block_n.header.block_hash())
-    })
-    .expect("Tip did not advance to block N");
+        wait_for_block_pushed_and_tip(30, info_before.stacks_tip_height + 1, &miner_pk, || {
+            signer_test.get_peer_info().stacks_tip
+        })
+        .expect("Timed out waiting for block N to be mined");
 
     info!("------------------------- Attempt to Mine Nakamoto Block N+1 -------------------------");
     // Propose a valid block, but force the miner to ignore the returned signatures and delay the block being
@@ -4212,14 +4229,10 @@ fn miner_recovers_when_broadcast_block_delay_across_tenures_occurs() {
         info_before.stacks_tip_height + 2
     );
     let block_n_2 =
-        wait_for_block_pushed_by_miner_key(30, info_before.stacks_tip_height + 2, &miner_pk)
-            .expect("Timed out waiting for block N+2 to be mined");
-
-    wait_for(30, || {
-        let info = signer_test.get_peer_info();
-        Ok(info.stacks_tip == block_n_2.header.block_hash())
-    })
-    .expect("Tip did not advance to block N+2");
+        wait_for_block_pushed_and_tip(30, info_before.stacks_tip_height + 2, &miner_pk, || {
+            signer_test.get_peer_info().stacks_tip
+        })
+        .expect("Timed out waiting for block N+2 to be mined");
     assert_eq!(
         block_n_2.header.parent_block_id,
         block_n_1.header.block_id()
```

### stacks-node/src/tests/signer/v0/reorg.rs
```diff
@@ -235,17 +235,18 @@ fn reorg_attempts_count_towards_miner_validity() {
     );
     // The signer should automatically attempt to mine a new block once the signers eventually tell it to abandon the previous block
     // It will accept it even though block proposal timeout is exceeded because the miner did manage to propose block N' BEFORE the timeout.
-    let block_n_1 =
-        wait_for_block_pushed_by_miner_key(30, block_proposal_n.header.chain_length + 1, &miner_pk)
-            .expect("Failed to get mined block N+1");
+    let block_n_1 = wait_for_block_pushed_and_tip(
+        30,
+        block_proposal_n.header.chain_length + 1,
+        &miner_pk,
+        || get_chain_info(&signer_test.running_nodes.conf).stacks_tip,
+    )
+    .expect("Failed to get mined block N+1");
     assert!(block_n_1
         .get_tenure_tx_payload()
         .unwrap()
         .cause
         .is_eq(&TenureChangeCause::BlockFound),);
-    let chain_after = get_chain_info(&signer_test.running_nodes.conf);
-
-    assert_eq!(chain_after.stacks_tip, block_n_1.header.block_hash());
     assert_eq!(
         block_n_1.header.chain_length,
         block_proposal_n_prime.header.chain_length + 1
@@ -530,17 +531,13 @@ fn allow_reorg_within_first_proposal_burn_block_timing_secs() {
         .expect("Failed to mine BTC block followed by Block N");
 
     let miner_1_block_n =
-        wait_for_block_pushed_by_miner_key(30, stacks_height_before + 1, &miner_pk_1)
-            .expect("Failed to get block N");
+        wait_for_block_pushed_and_tip(30, stacks_height_before + 1, &miner_pk_1, || {
+            get_chain_info(&conf_1).stacks_tip
+        })
+        .expect("Failed to get block N");
 
     let block_n_height = miner_1_block_n.header.chain_length;
     info!("Block N: {block_n_height}");
-    // Wait for the tip to advance before checking
-    wait_for(30, || {
-        let info = get_chain_info(&conf_1);
-        Ok(info.stacks_tip == miner_1_block_n.header.block_hash())
-    })
-    .expect("Tip did not advance to block N");
     assert_eq!(block_n_height, stacks_height_before + 1);
 
     // assure we have a successful sortition that miner 1 won
@@ -566,14 +563,12 @@ fn allow_reorg_within_first_proposal_burn_block_timing_secs() {
     info!("------------------------- Miner 2 Mines Block N+1 -------------------------");
     test_observer::clear();
     TEST_BROADCAST_PROPOSAL_STALL.set(vec![miner_pk_1.clone()]);
-    let miner_2_block_n_1 = wait_for_block_pushed_by_miner_key(30, block_n_height + 1, &miner_pk_2)
+    let miner_2_block_n_1 =
+        wait_for_block_pushed_and_tip(30, block_n_height + 1, &miner_pk_2, || {
+            get_chain_info(&conf_1).stacks_tip
+        })
         .expect("Failed to get block N+1");
 
-    assert_eq!(
-        get_chain_info(&conf_1).stacks_tip_height,
-        block_n_height + 1
-    );
-
     info!("------------------------- Miner 1 Wins the Next Tenure, Mines N+1' -------------------------");
     TEST_BROADCAST_PROPOSAL_STALL.set(vec![miner_pk_2]);
     miners
@@ -583,8 +578,10 @@ fn allow_reorg_within_first_proposal_burn_block_timing_secs() {
     verify_sortition_winner(&sortdb, &miner_pkh_1);
     TEST_BROADCAST_PROPOSAL_STALL.set(vec![]);
     let miner_1_block_n_1_prime =
-        wait_for_block_pushed_by_miner_key(30, block_n_height + 1, &miner_pk_1)
-            .expect("Failed to get block N+1'");
+        wait_for_block_pushed_and_tip(30, block_n_height + 1, &miner_pk_1, || {
+            miners.get_peer_info().stacks_tip
+        })
+        .expect("Failed to get block N+1'");
     assert_ne!(miner_1_block_n_1_prime, miner_2_block_n_1);
 
     info!("------------------------- Miner 1 Submits a Block Commit -------------------------");
@@ -594,24 +591,23 @@ fn allow_reorg_within_first_proposal_burn_block_timing_secs() {
 
     // Cannot use send_and_mine_transfer_tx as this relies on the peer's height
     miners.send_transfer_tx();
-    let _ = wait_for_block_pushed_by_miner_key(30, block_n_height + 2, &miner_pk_1)
+    let _miner_1_block_n_2_prime =
+        wait_for_block_pushed_and_tip(30, block_n_height + 2, &miner_pk_1, || {
+            miners.get_peer_info().stacks_tip
+        })
         .expect("Failed to get block N+2'");
 
     info!("------------------------- Miner 1 Mines N+3 in Next Tenure -------------------------");
 
     miners
         .mine_bitcoin_block_and_tenure_change_tx(&sortdb, TenureChangeCause::BlockFound, 60)
         .expect("Failed to mine BTC block followed by Block N+2");
-    let miner_1_block_n_3 = wait_for_block_pushed_by_miner_key(30, block_n_height + 3, &miner_pk_1)
+    let _miner_1_block_n_3 =
+        wait_for_block_pushed_and_tip(30, block_n_height + 3, &miner_pk_1, || {
+            miners.get_peer_info().stacks_tip
+        })
         .expect("Failed to get block N+3");
 
-    // Wait for the tip to advance before checking
-    wait_for(30, || {
-        let info = miners.get_peer_info();
-        Ok(info.stacks_tip == miner_1_block_n_3.header.block_hash())
-    })
-    .expect("Tip did not advance to block N+3");
-
     miners.shutdown();
 }
 
@@ -712,17 +708,13 @@ fn disallow_reorg_within_first_proposal_burn_block_timing_secs_but_more_than_one
         .expect("Failed to mine BTC block followed by Block N");
 
     let miner_1_block_n =
-        wait_for_block_pushed_by_miner_key(30, stacks_height_before + 1, &miner_pk_1)
-            .expect("Failed to get block N");
+        wait_for_block_pushed_and_tip(30, stacks_height_before + 1, &miner_pk_1, || {
+            get_chain_info(&conf_1).stacks_tip
+        })
+        .expect("Failed to get block N");
 
     let block_n_height = miner_1_block_n.header.chain_length;
     info!("Block N: {block_n_height}");
-    // Wait for the tip to advance before checking
-    wait_for(30, || {
-        let info = get_chain_info(&conf_1);
-        Ok(info.stacks_tip == miner_1_block_n.header.block_hash())
-    })
-    .expect("Tip did not advance to block N");
     assert_eq!(block_n_height, stacks_height_before + 1);
 
     // assure we have a successful sortition that miner 1 won
@@ -745,17 +737,14 @@ fn disallow_reorg_within_first_proposal_burn_block_timing_secs_but_more_than_one
     info!("------------------------- Miner 2 Mines Block N+1 -------------------------");
 
     fault_injection_unstall_miner();
-    let _ = wait_for_block_pushed_by_miner_key(30, block_n_height + 1, &miner_pk_2)
-        .expect("Failed to get block N+1");
+    let _ = wait_for_block_pushed_and_tip(30, block_n_height + 1, &miner_pk_2, || {
+        get_chain_info(&conf_1).stacks_tip
+    })
+    .expect("Failed to get block N+1");
 
     // assure we have a successful sortition that miner 2 won
     verify_sortition_winner(&sortdb, &miner_pkh_2);
 
-    assert_eq!(
-        get_chain_info(&conf_1).stacks_tip_height,
-        block_n_height + 1
-    );
-
     info!("------------------------- Miner 2 Mines N+2 and N+3 -------------------------");
     miners
         .send_and_mine_transfer_tx(30)
@@ -996,13 +985,11 @@ fn interrupt_miner_on_new_stacks_tip() {
     );
 
     info!("------------------------- Signers Accept Block N+1 -------------------------");
-    let miner_2_block_n_1 =
-        wait_for_block_pushed_by_miner_key(30, stacks_height_before + 2, &miner_pk_2)
-            .expect("Failed to see block acceptance of Miner 2's Block N+1");
-    assert_eq!(
-        miner_2_block_n_1.header.block_hash(),
-        miners.get_peer_stacks_tip()
-    );
+    let _miner_2_block_n_1 =
+        wait_for_block_pushed_and_tip(30, stacks_height_before + 2, &miner_pk_2, || {
+            miners.get_peer_info().stacks_tip
+        })
+        .expect("Failed to see block acceptance of Miner 2's Block N+1");
 
     info!("------------------------- Next Tenure Builds on N+1 -------------------------");
     miners.ensure_commit_miner_1(&sortdb);
@@ -1119,15 +1106,10 @@ fn global_acceptance_depends_on_block_announcement() {
 
     // Ensure that the block was accepted globally so the stacks tip has advanced to N
     let block_n =
-        wait_for_block_pushed_by_miner_key(30, info_before.stacks_tip_height + 1, &miner_pk)
-            .expect("Timed out waiting for block N to be mined");
-
-    // Wait for the tip to advance before checking
-    wait_for(30, || {
-        let info = signer_test.get_peer_info();
-        Ok(info.stacks_tip == block_n.header.block_hash())
-    })
-    .expect("Tip did not advance to block N");
+        wait_for_block_pushed_and_tip(30, info_before.stacks_tip_height + 1, &miner_pk, || {
+            signer_test.get_peer_info().stacks_tip
+        })
+        .expect("Timed out waiting for block N to be mined");
 
     info!("------------------------- Mine Nakamoto Block N+1 -------------------------");
     // Make less than 30% of the signers reject the block and ensure it is accepted by the node, but not announced.
@@ -1194,8 +1176,10 @@ fn global_acceptance_depends_on_block_announcement() {
     info!("------------------------- Waiting for block N+1' -------------------------");
     // Cannot use wait_for_block_pushed_by_miner_key as we could have more than one block proposal for the same height from the miner
     let sister_block =
-        wait_for_block_pushed_by_miner_key(30, info_before.stacks_tip_height + 1, &miner_pk)
-            .expect("Failed to get pushed sister block");
+        wait_for_block_pushed_and_tip(30, info_before.stacks_tip_height + 1, &miner_pk, || {
+            signer_test.get_peer_info().stacks_tip
+        })
+        .expect("Failed to get pushed sister block");
     assert_ne!(
         sister_block.header.signer_signature_hash(),
         block_n_1.header.signer_signature_hash()
@@ -1204,13 +1188,6 @@ fn global_acceptance_depends_on_block_announcement() {
         sister_block.header.chain_length,
         block_n_1.header.chain_length
     );
-
-    // Wait for the tip to advance before checking
-    wait_for(30, || {
-        let info = signer_test.get_peer_info();
-        Ok(info.stacks_tip == sister_block.header.block_hash())
-    })
-    .expect("Tip did not advance to sister block");
     // Assert the block was mined and the tip has changed.
     let info_after = signer_test.get_peer_info();
     assert_eq!(
@@ -1321,11 +1298,11 @@ fn no_reorg_due_to_successive_block_validation_ok() {
         .expect("Failed to mine Block N");
     // assure we have a successful sortition that miner 1 won
     verify_sortition_winner(&sortdb, &miner_pkh_1);
-    let block_n = wait_for_block_pushed_by_miner_key(30, stacks_height_before + 1, &miner_pk_1)
-        .expect("Failed to find block N");
+    let block_n = wait_for_block_pushed_and_tip(30, stacks_height_before + 1, &miner_pk_1, || {
+        miners.get_peer_info().stacks_tip
+    })
+    .expect("Failed to find block N");
     let block_n_signature_hash = block_n.header.signer_signature_hash();
-
-    assert_eq!(miners.get_peer_stacks_tip(), block_n.header.block_hash());
     debug!("Miner 1 mined block N: {block_n_signature_hash}");
 
     info!("------------------------- Pause Block Validation Response of N+1 -------------------------");
@@ -1452,14 +1429,10 @@ fn no_reorg_due_to_successive_block_validation_ok() {
     // Miner 2 will see block N+1 as a valid block and reattempt to mine N+2 on top.
     info!("------------------------- Confirm N+2 Accepted ------------------------");
     let block_n_2 =
-        wait_for_block_pushed_by_miner_key(30, block_n_1.header.chain_length + 1, &miner_pk_2)
-            .expect("Failed to find block N+2");
-    // Wait for the tip to advance before checking
-    wait_for(30, || {
-        let info = get_chain_info(&conf_1);
-        Ok(info.stacks_tip == block_n_2.header.block_hash())
-    })
-    .expect("Tip did not advance to block N+2");
+        wait_for_block_pushed_and_tip(30, block_n_1.header.chain_length + 1, &miner_pk_2, || {
+            get_chain_info(&conf_1).stacks_tip
+        })
+        .expect("Failed to find block N+2");
     info!("------------------------- Confirm Stacks Chain is As Expected ------------------------");
     let info_after = get_chain_info(&conf_1);
     assert_eq!(info_after.stacks_tip_height, starting_peer_height + 3);
@@ -2625,15 +2598,11 @@ fn locally_accepted_blocks_overriden_by_global_rejection() {
     let tx = submit_tx(&http_origin, &transfer_tx);
     sender_nonce += 1;
     info!("Submitted tx {tx} in to mine block N");
-    let block_n =
-        wait_for_block_pushed_by_miner_key(30, info_before.stacks_tip_height + 1, &miner_pk)
-            .expect("Timed out waiting for block N to be mined");
-    // Wait for the tip to actually advance to block N before proceeding
-    wait_for(30, || {
-        let info = signer_test.get_peer_info();
-        Ok(info.stacks_tip == block_n.header.block_hash())
-    })
-    .expect("Tip did not advance to block N");
+    let _block_n =
+        wait_for_block_pushed_and_tip(30, info_before.stacks_tip_height + 1, &miner_pk, || {
+            signer_test.get_peer_info().stacks_tip
+        })
+        .expect("Timed out waiting for block N to be mined");
 
     info!("------------------------- Attempt to Mine Nakamoto Block N+1 -------------------------");
     // Make half of the signers reject the block proposal by the miner to ensure its marked globally rejected
@@ -2686,19 +2655,13 @@ fn locally_accepted_blocks_overriden_by_global_rejection() {
     let tx = submit_tx(&http_origin, &transfer_tx);
     info!("Submitted tx {tx} to mine block N+1'");
 
-    let block_n_1_prime = wait_for_block_pushed_by_miner_key(
+    let block_n_1_prime = wait_for_block_pushed_and_tip(
         short_timeout_secs,
         info_before.stacks_tip_height + 1,
         &miner_pk,
+        || signer_test.get_peer_info().stacks_tip,
     )
     .expect("Timed out waiting for block N+1' to be mined");
-
-    // Wait for the tip to advance before checking
-    wait_for(30, || {
-        let info = signer_test.get_peer_info();
-        Ok(info.stacks_tip == block_n_1_prime.header.block_hash())
-    })
-    .expect("Tip did not advance to block N+1'");
     assert_ne!(block_n_1_prime, proposed_block_n_1);
 
     signer_test.shutdown();
@@ -2778,15 +2741,11 @@ fn locally_rejected_blocks_overriden_by_global_acceptance() {
     let tx = submit_tx(&http_origin, &transfer_tx);
     sender_nonce += 1;
     info!("Submitted tx {tx} in to mine block N");
-    let block_n =
-        wait_for_block_pushed_by_miner_key(30, info_before.stacks_tip_height + 1, &miner_pk)
-            .expect("Timed out waiting for block N to be mined");
-    // Wait for the tip to actually advance to block N before proceeding
-    wait_for(30, || {
-        let info = signer_test.get_peer_info();
-        Ok(info.stacks_tip == block_n.header.block_hash())
-    })
-    .expect("Tip did not advance to block N");
+    let _block_n =
+        wait_for_block_pushed_and_tip(30, info_before.stacks_tip_height + 1, &miner_pk, || {
+            signer_test.get_peer_info().stacks_tip
+        })
+        .expect("Timed out waiting for block N to be mined");
 
     info!("------------------------- Mine Nakamoto Block N+1 -------------------------");
     // Make less than 30% of the signers reject the block and ensure it is STILL marked globally accepted
@@ -2813,8 +2772,10 @@ fn locally_rejected_blocks_overriden_by_global_acceptance() {
     info!("Submitted tx {tx} in to mine block N+1");
     // The rejecting signers will reject the block, but it will still be accepted globally
     let block_n_1 =
-        wait_for_block_pushed_by_miner_key(30, info_before.stacks_tip_height + 1, &miner_pk)
-            .expect("Timed out waiting for block N+1 to be mined");
+        wait_for_block_pushed_and_tip(30, info_before.stacks_tip_height + 1, &miner_pk, || {
+            signer_test.get_peer_info().stacks_tip
+        })
+        .expect("Timed out waiting for block N+1 to be mined");
 
     wait_for_block_rejections_from_signers(
         short_timeout,
@@ -2823,13 +2784,6 @@ fn locally_rejected_blocks_overriden_by_global_acceptance() {
     )
     .expect("Timed out waiting for block rejection of N+1");
 
-    // Wait for the tip to advance before checking
-    wait_for(30, || {
-        let info = signer_test.get_peer_info();
-        Ok(info.stacks_tip == block_n_1.header.block_hash())
-    })
-    .expect("Tip did not advance to block N+1");
-
     info!("------------------------- Test Mine Nakamoto Block N+2 -------------------------");
     // Ensure that all signers accept the block proposal N+2
     let info_before = signer_test.get_peer_info();
@@ -2846,15 +2800,16 @@ fn locally_rejected_blocks_overriden_by_global_acceptance() {
     );
     let tx = submit_tx(&http_origin, &transfer_tx);
     info!("Submitted tx {tx} in to mine block N+2");
-    let block_n_2 =
-        wait_for_block_pushed_by_miner_key(30, info_before.stacks_tip_height + 1, &miner_pk)
-            .expect("Timed out waiting for block N+2 to be pushed");
+    let _block_n_2 =
+        wait_for_block_pushed_and_tip(30, info_before.stacks_tip_height + 1, &miner_pk, || {
+            signer_test.get_peer_info().stacks_tip
+        })
+        .expect("Timed out waiting for block N+2 to be pushed");
     let info_after = signer_test.get_peer_info();
     assert_eq!(
         info_before.stacks_tip_height + 1,
         info_after.stacks_tip_height,
     );
-    assert_eq!(info_after.stacks_tip, block_n_2.header.block_hash());
     signer_test.shutdown();
 }
 
@@ -2933,18 +2888,14 @@ fn reorg_locally_accepted_blocks_across_tenures_succeeds() {
     let txid = submit_tx(&http_origin, &transfer_tx);
     sender_nonce += 1;
     let block_n =
-        wait_for_block_pushed_by_miner_key(30, info_before.stacks_tip_height + 1, &miner_pk)
-            .expect("Timed out waiting for block N to be mined");
+        wait_for_block_pushed_and_tip(30, info_before.stacks_tip_height + 1, &miner_pk, || {
+            signer_test.get_peer_info().stacks_tip
+        })
+        .expect("Timed out waiting for block N to be mined");
     assert!(block_n
         .txs
         .iter()
         .any(|tx| { tx.txid().to_string() == txid }));
-    // Wait for the tip to advance before checking
-    wait_for(30, || {
-        let info = signer_test.get_peer_info();
-        Ok(info.stacks_tip == block_n.header.block_hash())
-    })
-    .expect("Tip did not advance to block N");
 
     info!("------------------------- Attempt to Mine Nakamoto Block N+1 at Height {} -------------------------", info_before.stacks_tip_height + 2);
     // Make more than >70% of the signers ignore the block proposal to ensure it it is not globally accepted/rejected
@@ -3030,14 +2981,10 @@ fn reorg_locally_accepted_blocks_across_tenures_succeeds() {
     TEST_MINE_SKIP.set(false);
 
     let block_n_1_prime =
-        wait_for_block_pushed_by_miner_key(30, info_before.stacks_tip_height + 1, &miner_pk)
-            .expect("Timed out waiting for block N+1' to be mined");
-    // Wait for the tip to advance before checking
-    wait_for(30, || {
-        let info = signer_test.get_peer_info();
-        Ok(info.stacks_tip == block_n_1_prime.header.block_hash())
-    })
-    .expect("Tip did not advance to block N+1'");
+        wait_for_block_pushed_and_tip(30, info_before.stacks_tip_height + 1, &miner_pk, || {
+            signer_test.get_peer_info().stacks_tip
+        })
+        .expect("Timed out waiting for block N+1' to be mined");
     assert_ne!(
         block_n_1_prime.header.signer_signature_hash(),
         block_n_1_proposal.header.signer_signature_hash()
@@ -3052,14 +2999,10 @@ fn reorg_locally_accepted_blocks_across_tenures_succeeds() {
         info_before.stacks_tip_height + 2
     );
     let block_n_2 =
-        wait_for_block_pushed_by_miner_key(30, info_before.stacks_tip_height + 2, &miner_pk)
-            .expect("Timed out waiting for block N+2 to be mined");
-
-    wait_for(30, || {
-        let info = signer_test.get_peer_info();
-        Ok(info.stacks_tip == block_n_2.header.block_hash())
-    })
-    .expect("Tip did not advance to block N+2");
+        wait_for_block_pushed_and_tip(30, info_before.stacks_tip_height + 2, &miner_pk, || {
+            signer_test.get_peer_info().stacks_tip
+        })
+        .expect("Timed out waiting for block N+2 to be mined");
     assert_eq!(block_n_2.header.parent_block_id, block_n_1_prime.block_id());
     signer_test.shutdown();
 }
@@ -3140,14 +3083,11 @@ fn reorg_locally_accepted_blocks_across_tenures_fails() {
     let tx = submit_tx(&http_origin, &transfer_tx);
     sender_nonce += 1;
     info!("Submitted tx {tx} in to mine block N");
-    let block_n =
-        wait_for_block_pushed_by_miner_key(30, info_before.stacks_tip_height + 1, &miner_pk)
-            .expect("Timed out waiting for block N to be mined");
-    // Due to a potential race condition in processing and block pushed...have to wait
-    wait_for(30, || {
-        Ok(signer_test.get_peer_info().stacks_tip == block_n.header.block_hash())
-    })
-    .expect("Tip did not advance to block N");
+    let _block_n =
+        wait_for_block_pushed_and_tip(30, info_before.stacks_tip_height + 1, &miner_pk, || {
+            signer_test.get_peer_info().stacks_tip
+        })
+        .expect("Timed out waiting for block N to be mined");
 
     info!("------------------------- Attempt to Mine Nakamoto Block N+1 -------------------------");
     // Make more than >70% of the signers ignore the block proposal to ensure it it is not globally accepted/rejected
@@ -3582,7 +3522,7 @@ fn reorging_signers_capitulate_to_nonreorging_signers_during_tenure_fork() {
     TEST_BROADCAST_PROPOSAL_STALL.set(vec![miner_pk_1.clone()]);
     TEST_BLOCK_ANNOUNCE_STALL.set(true);
 
-    miners.ensure_commit_miner_1(&sortdb); 
+    miners.ensure_commit_miner_1(&sortdb);
 
     info!("------------------------- Miner 1 Wins Tenure B -------------------------");
     miners
@@ -3687,8 +3627,10 @@ fn reorging_signers_capitulate_to_nonreorging_signers_during_tenure_fork() {
     info!("--------------- Miner 1 Extends Tenure B over Tenure C ---------------");
     TEST_BROADCAST_PROPOSAL_STALL.set(vec![]);
     let _tenure_extend_block =
-        wait_for_block_pushed_by_miner_key(30, tip_b.stacks_block_height + 1, &miner_pk_1)
-            .expect("Failed to mine miner 1's tenure extend block");
+        wait_for_block_pushed_and_tip(30, tip_b.stacks_block_height + 1, &miner_pk_1, || {
+            miners.get_peer_info().stacks_tip
+        })
+        .expect("Failed to mine miner 1's tenure extend block");
 
     info!("------------------------- Miner 1 Mines Another Block -------------------------");
     miners
@@ -3810,18 +3752,13 @@ fn mark_miner_as_invalid_if_reorg_is_rejected_v1() {
     verify_sortition_winner(&sortdb, &miner_pkh_1);
 
     let block_n =
-        wait_for_block_pushed_by_miner_key(30, info_before.stacks_tip_height + 1, &miner_pk_1)
-            .expect("Failed to get block N");
+        wait_for_block_pushed_and_tip(30, info_before.stacks_tip_height + 1, &miner_pk_1, || {
+            get_chain_info(&conf_1).stacks_tip
+        })
+        .expect("Failed to get block N");
     let block_n_height = block_n.header.chain_length;
     info!("Block N: {block_n_height}");
 
-    // Wait for the tip to advance before checking
-    wait_for(30, || {
-        let info = get_chain_info(&conf_1);
-        Ok(info.stacks_tip == block_n.header.block_hash())
-    })
-    .expect("Tip did not advance to block N");
-
     info!("------------------------- Miner 2 Submits a Block Commit -------------------------");
     miners.ensure_commit_miner_2(&sortdb);
 
@@ -3839,15 +3776,10 @@ fn mark_miner_as_invalid_if_reorg_is_rejected_v1() {
     info!("------------------------- Miner 2 Mines Block N+1 -------------------------");
     fault_injection_unstall_miner();
 
-    let block_n_1 = wait_for_block_pushed_by_miner_key(30, block_n_height + 1, &miner_pk_2)
-        .expect("Failed to get block N+1");
-
-    // Wait for the tip to advance before checking
-    wait_for(30, || {
-        let info = get_chain_info(&conf_1);
-        Ok(info.stacks_tip == block_n_1.header.block_hash())
+    let _block_n_1 = wait_for_block_pushed_and_tip(30, block_n_height + 1, &miner_pk_2, || {
+        get_chain_info(&conf_1).stacks_tip
     })
-    .expect("Tip did not advance to block N+1");
+    .expect("Failed to get block N+1");
 
     // Wait for both chains to be in sync
     miners.wait_for_chains(30);
@@ -4569,20 +4501,16 @@ fn new_tenure_while_validating_previous_scenario() {
     info!("----- Mining BlockFound -----");
     // Now, wait for miner B to propose a new block
     let block_pushed =
-        wait_for_block_pushed_by_miner_key(30, stacks_height_before_stall + 2, &miner_pk)
-            .expect("Timed out waiting for block N+2 to be mined");
+        wait_for_block_pushed_and_tip(30, stacks_height_before_stall + 2, &miner_pk, || {
+            signer_test.get_peer_info().stacks_tip
+        })
+        .expect("Timed out waiting for block N+2 to be mined");
     // Ensure that we didn't tenure extend
     assert!(block_pushed
         .try_get_tenure_change_payload()
         .unwrap()
         .cause
         .is_eq(&TenureChangeCause::BlockFound));
-    // Wait for the tip to advance before checking
-    wait_for(30, || {
-        let info = signer_test.get_peer_info();
-        Ok(info.stacks_tip == block_pushed.header.block_hash())
-    })
-    .expect("Tip did not advance to block N+2");
 
     info!("------------------------- Shutdown -------------------------");
     signer_test.shutdown();
```

### stacks-node/src/tests/signer/v0/signers_consider_late_proposals.rs
```diff
@@ -26,10 +26,9 @@ use tracing_subscriber::{fmt, EnvFilter};
 
 use super::SignerTest;
 use crate::nakamoto_node::stackerdb_listener::TEST_IGNORE_SIGNERS;
-use crate::tests::nakamoto_integrations::wait_for;
 use crate::tests::signer::v0::{
     wait_for_block_acceptance_from_signers, wait_for_block_pre_commits_from_signers,
-    wait_for_block_proposal, wait_for_block_pushed_by_miner_key,
+    wait_for_block_proposal, wait_for_block_pushed_and_tip,
 };
 
 #[test]
@@ -110,12 +109,10 @@ fn signers_reprocess_late_block_proposals_pre_commits() {
     wait_for_block_acceptance_from_signers(30, &sighash, &all_signers)
         .expect("All signers should have accepted the block proposal after it was reproposed");
     info!("------------------------- Wait for block pushed -------------------------");
-    wait_for_block_pushed_by_miner_key(30, expected_height, &miner_pk)
-        .expect("Block should have been pushed to the node after being accepted by all signers");
-    wait_for(30, || {
-        Ok(signer_test.get_peer_info().stacks_tip_height == expected_height)
+    wait_for_block_pushed_and_tip(30, expected_height, &miner_pk, || {
+        signer_test.get_peer_info().stacks_tip
     })
-    .expect("Node should have advanced to expected height after block acceptance");
+    .expect("Block should have been pushed to the node after being accepted by all signers");
 }
 
 #[test]
@@ -209,10 +206,8 @@ fn signers_reprocess_late_block_proposals_signatures() {
     wait_for_block_acceptance_from_signers(30, &sighash, &ignoring_signers)
         .expect("Ignoring signer should have accepted the block proposal after it was reproposed");
     info!("------------------------- Wait for block pushed -------------------------");
-    wait_for_block_pushed_by_miner_key(30, expected_height, &miner_pk)
-        .expect("Block should have been pushed to the node after the threshold was exceeded by the late signer");
-    wait_for(30, || {
-        Ok(signer_test.get_peer_info().stacks_tip_height == expected_height)
+    wait_for_block_pushed_and_tip(30, expected_height, &miner_pk, || {
+        signer_test.get_peer_info().stacks_tip
     })
-    .expect("Node should have advanced to expected height after block acceptance");
+    .expect("Block should have been pushed to the node after the threshold was exceeded by the late signer");
 }
```

### stacks-node/src/tests/signer/v0/tenure_extend.rs
```diff
@@ -2219,9 +2219,11 @@ fn prev_miner_extends_if_incoming_miner_fails_to_mine_success() {
     info!("------------------------- Wait for Miner 1's Block N+1 to be Mined ------------------------";
         "stacks_height_before" => %stacks_height_before);
 
-    let miner_1_block_n_1 =
-        wait_for_block_pushed_by_miner_key(30, stacks_height_before + 1, &miner_pk_1)
-            .expect("Timed out waiting for block proposal N+1 from miner 1");
+    let _miner_1_block_n_1 =
+        wait_for_block_pushed_and_tip(30, stacks_height_before + 1, &miner_pk_1, || {
+            miners.get_peer_info().stacks_tip
+        })
+        .expect("Timed out waiting for block proposal N+1 from miner 1");
 
     let miner_2_block_n_1 =
         wait_for_block_proposal_block(30, stacks_height_before + 1, &miner_pk_2)
@@ -2234,12 +2236,6 @@ fn prev_miner_extends_if_incoming_miner_fails_to_mine_success() {
     )
     .expect("Timed out waiting for global rejection of Miner 2's block N+1'");
 
-    wait_for(30, || {
-        let info = miners.get_peer_info();
-        Ok(info.stacks_tip == miner_1_block_n_1.header.block_hash())
-    })
-    .expect("Tip did not advance to expected block");
-
     info!(
         "------------------------- Verify Tenure Change Extend Tx in Miner 1's Block N+1 -------------------------"
     );
@@ -2420,15 +2416,11 @@ fn prev_miner_extends_if_incoming_miner_fails_to_mine_failure() {
     // Miner 2's proposed block should get approved and pushed.
     // Use wait_for_block_pushed_by_miner_key to avoid matching a stale proposal
     // (there may be multiple proposals for the same height).
-    let miner_2_block_n_1 =
-        wait_for_block_pushed_by_miner_key(60, stacks_height_before + 1, &miner_pk_2)
-            .expect("Timed out waiting for Block N+1 to be pushed");
-
-    wait_for(30, || {
-        let info = miners.get_peer_info();
-        Ok(info.stacks_tip == miner_2_block_n_1.header.block_hash())
-    })
-    .expect("Tip did not advance to expected block");
+    let _miner_2_block_n_1 =
+        wait_for_block_pushed_and_tip(60, stacks_height_before + 1, &miner_pk_2, || {
+            miners.get_peer_info().stacks_tip
+        })
+        .expect("Timed out waiting for Block N+1 to be pushed");
 
     info!(
         "------------------------- Verify BlockFound in Miner 2's Block N+1 -------------------------"
@@ -2565,15 +2557,11 @@ fn prev_miner_will_not_attempt_to_extend_if_incoming_miner_produces_a_block() {
 
     info!("------------------------- Get Miner 2's N+1 block -------------------------");
 
-    let miner_2_block_n_1 =
-        wait_for_block_pushed_by_miner_key(60, stacks_height_before + 1, &miner_pk_2)
-            .expect("Timed out waiting for N+1 block to be approved");
-
-    wait_for(30, || {
-        let info = miners.get_peer_info();
-        Ok(info.stacks_tip == miner_2_block_n_1.header.block_hash())
-    })
-    .expect("Tip did not advance to expected block");
+    let _miner_2_block_n_1 =
+        wait_for_block_pushed_and_tip(60, stacks_height_before + 1, &miner_pk_2, || {
+            miners.get_peer_info().stacks_tip
+        })
+        .expect("Timed out waiting for N+1 block to be approved");
     let peer_info = miners.get_peer_info();
 
     let stacks_height_before = peer_info.stacks_tip_height;
@@ -3623,14 +3611,11 @@ fn non_blocking_minority_configured_to_favour_test(variant: NonBlockingMinorityV
         test_observer::clear();
         TEST_BROADCAST_PROPOSAL_STALL.set(vec![]);
 
-        let miner_1_block_n_1 =
-            wait_for_block_pushed_by_miner_key(30, stacks_height_before + 1, &miner_pk_1)
-                .expect("Timed out waiting for Miner 1 to mine N+1");
-        wait_for(30, || {
-            let info = miners.get_peer_info();
-            Ok(info.stacks_tip == miner_1_block_n_1.header.block_hash())
-        })
-        .expect("Tip did not advance to expected block");
+        let _miner_1_block_n_1 =
+            wait_for_block_pushed_and_tip(30, stacks_height_before + 1, &miner_pk_1, || {
+                miners.get_peer_info().stacks_tip
+            })
+            .expect("Timed out waiting for Miner 1 to mine N+1");
 
         info!(
             "------------------------- Verify Extended in Miner 1's Block N+1 -------------------------"
@@ -3680,13 +3665,10 @@ fn non_blocking_minority_configured_to_favour_test(variant: NonBlockingMinorityV
         TEST_BROADCAST_PROPOSAL_STALL.set(vec![]);
 
         let miner_2_block_n_1 =
-            wait_for_block_pushed_by_miner_key(30, stacks_height_before + 1, &miner_pk_2)
-                .expect("Miner 2's block N+1 was not mined");
-        wait_for(30, || {
-            let info = miners.get_peer_info();
-            Ok(info.stacks_tip == miner_2_block_n_1.header.block_hash())
-        })
-        .expect("Tip did not advance to expected block");
+            wait_for_block_pushed_and_tip(30, stacks_height_before + 1, &miner_pk_2, || {
+                miners.get_peer_info().stacks_tip
+            })
+            .expect("Miner 2's block N+1 was not mined");
 
         if matches!(variant, NonBlockingMinorityVariant::FavourPrevMiner) {
             info!(
@@ -3729,14 +3711,10 @@ fn non_blocking_minority_configured_to_favour_test(variant: NonBlockingMinorityV
         &miner_pk_2
     };
     let block_n_2 =
-        wait_for_block_pushed_by_miner_key(30, stacks_height_before + 1, continuing_miner_pk)
-            .expect("Timed out waiting for block N+2");
-
-    wait_for(30, || {
-        let info = miners.get_peer_info();
-        Ok(info.stacks_tip == block_n_2.header.block_hash())
-    })
-    .expect("Tip did not advance to expected block");
+        wait_for_block_pushed_and_tip(30, stacks_height_before + 1, continuing_miner_pk, || {
+            miners.get_peer_info().stacks_tip
+        })
+        .expect("Timed out waiting for block N+2");
 
     // V1 variant additionally verifies minority rejection for N+2
     if matches!(variant, NonBlockingMinorityVariant::FavourPrevMinerV1) {
@@ -4355,13 +4333,10 @@ fn continue_after_fast_block_no_sortition() {
     info!("------------------------- Wait for Miner B's Block N+2 -------------------------");
 
     let miner_2_block_n_2 =
-        wait_for_block_pushed_by_miner_key(30, stacks_height_before + 2, &miner_pk_2)
-            .expect("Did not mine Miner 2's Block N+2");
-    wait_for(30, || {
-        let info = miners.get_peer_info();
-        Ok(info.stacks_tip == miner_2_block_n_2.header.block_hash())
-    })
-    .expect("Tip did not advance to expected block");
+        wait_for_block_pushed_and_tip(30, stacks_height_before + 2, &miner_pk_2, || {
+            miners.get_peer_info().stacks_tip
+        })
+        .expect("Did not mine Miner 2's Block N+2");
 
     info!("------------------------- Verify Miner B's Block N+2 -------------------------");
     assert!(miner_2_block_n_2
@@ -4379,7 +4354,10 @@ fn continue_after_fast_block_no_sortition() {
 
     info!("------------------------- Verify Miner B's Block N+3 -------------------------");
 
-    let block_n_3 = wait_for_block_pushed_by_miner_key(30, stacks_height_before + 3, &miner_pk_2)
+    let block_n_3 =
+        wait_for_block_pushed_and_tip(30, stacks_height_before + 3, &miner_pk_2, || {
+            miners.get_peer_info().stacks_tip
+        })
         .expect("Did not mine Miner 2's Block N+3");
     assert!(block_n_3
         .txs
```
