# [?] fix(epoch-sync): reject malicious proofs instead of overflow panic (#15921)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2026-06-16
Source: https://github.com/near/nearcore/commit/1ab8ed40d320d155a04d7b82aa745e73e773cc91
Type: security-commit

## Details
fix(epoch-sync): reject malicious proofs instead of overflow panic (#15921)

A peer that a bootstrapping node selects as its epoch-sync source can
crash the node with an arithmetic overflow panic on attacker-controlled
`u64` fields in the proof. Two such sites, both reachable before the
offending value is validated:

- `partial_merkle_tree_for_first_block.size() + 1` in
`verify_current_epoch_data`: `size = u64::MAX` overflows before the
well-formedness check.
- `last_final_block_header.height() + 1` in `verify_block_endorsements`:
`height = u64::MAX` overflows before any signature check.

Both now use `checked_add` and return `InvalidEpochSyncProof` on
overflow. Adds regression tests for each.

## Patch
### chain/client/src/sync/epoch.rs
```diff
@@ -422,8 +422,10 @@ impl EpochSync {
         // needs to be valid and have the correct root.
         //
         // Note that the block_ordinal in the header is 1-based, so we need to add 1 to the size.
-        if current_epoch.partial_merkle_tree_for_first_block.size() + 1
-            != first_block_header.block_ordinal()
+        // Use checked_add so an attacker-controlled size of u64::MAX cannot trigger an arithmetic
+        // overflow panic (which would crash a bootstrapping node) before the is_well_formed check.
+        if current_epoch.partial_merkle_tree_for_first_block.size().checked_add(1)
+            != Some(first_block_header.block_ordinal())
         {
             return Err(Error::InvalidEpochSyncProof(
                 "invalid size in partial_merkle_tree_for_first_block".to_string(),
@@ -514,18 +516,24 @@ impl EpochSync {
             )));
         }
 
-        let message_to_sign = Approval::get_data_for_sig(
-            &ApprovalInner::Endorsement(prev_block_hash),
-            block_height + 1,
-        );
+        // `block_height` comes from an attacker-controlled header in the proof and is not bounded
+        // before this point, so use checked_add to avoid an arithmetic overflow panic (which would
+        // crash a bootstrapping node) when the height is u64::MAX.
+        let Some(target_height) = block_height.checked_add(1) else {
+            return Err(Error::InvalidEpochSyncProof(format!(
+                "block height {block_height} too large in epoch sync proof"
+            )));
+        };
+        let message_to_sign =
+            Approval::get_data_for_sig(&ApprovalInner::Endorsement(prev_block_hash), target_height);
 
         let mut total_stake = Balance::ZERO;
         let mut endorsed_stake = Balance::ZERO;
 
         for (validator, may_be_signature) in block_producers.iter().zip(endorsements.iter()) {
             if let Some(signature) = may_be_signature {
                 if !signature.verify(&message_to_sign, validator.public_key()) {
-                    return Err(near_chain::Error::InvalidEpochSyncProof(format!(
+                    return Err(Error::InvalidEpochSyncProof(format!(
                         "Invalid signature for block {} from validator {:?}",
                         block_height,
                         validator.account_id()
@@ -659,3 +667,25 @@ impl Handler<EpochSyncResponseMessage> for ClientActor {
         }
     }
 }
+
+#[cfg(test)]
+mod tests {
+    use super::EpochSync;
+    use near_chain::Error;
+    use near_primitives::hash::CryptoHash;
+
+    /// Regression test: an attacker-supplied epoch sync proof may carry a block header whose height
+    /// is u64::MAX. `verify_block_endorsements` computes `block_height + 1`, which would overflow
+    /// and crash a bootstrapping node. It must instead be rejected as an invalid proof.
+    #[test]
+    fn verify_block_endorsements_rejects_max_height() {
+        let err = EpochSync::verify_block_endorsements(CryptoHash::default(), u64::MAX, &[], &[])
+            .unwrap_err();
+        match &err {
+            Error::InvalidEpochSyncProof(msg) => {
+                assert!(msg.contains("too large"), "unexpected message: {msg}");
+            }
+            _ => panic!("expected InvalidEpochSyncProof, got: {err}"),
+        }
+    }
+}
```

### test-loop-tests/src/tests/sync/epoch_sync.rs
```diff
@@ -3,6 +3,7 @@ use crate::setup::env::TestLoopEnv;
 use crate::utils::account::create_account_id;
 use crate::utils::node::TestLoopNode;
 use crate::utils::transactions::{BalanceMismatchError, execute_money_transfers};
+use borsh::BorshDeserialize;
 use itertools::Itertools;
 use near_async::time::Duration;
 use near_chain::ChainStoreAccess;
@@ -14,6 +15,7 @@ use near_epoch_manager::epoch_sync::{
 };
 use near_o11y::testonly::init_test_logger;
 use near_primitives::epoch_sync::EpochSyncProof;
+use near_primitives::merkle::PartialMerkleTree;
 use near_primitives::shard_layout::ShardLayout;
 use near_primitives::types::{AccountId, Balance, BlockHeightDelta};
 use near_primitives::version::{PROTOCOL_VERSION, ProtocolFeature};
@@ -400,3 +402,40 @@ fn slow_test_epoch_sync_proof_rejects_wrong_epoch_id_middle_epoch() {
         _ => panic!("expected InvalidEpochSyncProof, got: {err}"),
     }
 }
+
+#[test]
+// TODO(spice-test): Assess if this test is relevant for spice and if yes fix it.
+#[cfg_attr(feature = "protocol_feature_spice", ignore)]
+fn slow_test_epoch_sync_proof_rejects_max_size_partial_merkle_tree() {
+    init_test_logger();
+    let env = setup_initial_blockchain(20);
+
+    let client_handle = env.node_datas[0].client_sender.actor_handle();
+    let client = &env.test_loop.data.get(&client_handle).client;
+    let epoch_sync = &client.sync_handler.epoch_sync;
+    let epoch_manager = client.epoch_manager.as_ref();
+
+    let proof = env.derive_epoch_sync_proof(0).into_v1();
+    epoch_sync.verify_proof(&proof, epoch_manager).unwrap();
+
+    // Regression test: a partial merkle tree whose size is u64::MAX must be rejected gracefully,
+    // not crash the node via an arithmetic overflow on `size() + 1` during verification.
+    let mut tampered = proof;
+    let path = tampered.current_epoch.partial_merkle_tree_for_first_block.get_path().to_vec();
+    // `PartialMerkleTree` is borsh-encoded as `(path, size)` and the `size` field has no public
+    // setter, so rebuild it via a borsh round-trip with `size` set to u64::MAX.
+    let bytes = borsh::to_vec(&(path, u64::MAX)).unwrap();
+    tampered.current_epoch.partial_merkle_tree_for_first_block =
+        PartialMerkleTree::try_from_slice(&bytes).unwrap();
+
+    let err = epoch_sync.verify_proof(&tampered, epoch_manager).unwrap_err();
+    match &err {
+        Error::InvalidEpochSyncProof(msg) => {
+            assert!(
+                msg.contains("invalid size in partial_merkle_tree_for_first_block"),
+                "unexpected message: {msg}"
+            );
+        }
+        _ => panic!("expected InvalidEpochSyncProof, got: {err}"),
+    }
+}
```
