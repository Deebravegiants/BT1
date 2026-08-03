No vulnerability found for this question.

The `CrossShardCommitSender::send_remote_update_for_success` logic in `aptos-move/aptos-vm/src/sharded_block_executor/cross_shard_client.rs` correctly branches on `round_id == GLOBAL_ROUND_ID` to call `send_global_msg` versus `send_cross_shard_msg`. [1](#0-0) 

Several reasons this doesn't constitute a custody-grade finding:

1. **Round assignment is not attacker-controlled transaction input.** The `(shard_id, round_id)` values stored in `dependent_edges` come from `sub_block.txn_with_index_iter()` and `cross_shard_dependencies.dependent_edges()`, which are populated by the block partitioner's own static analysis of storage locations/access patterns during block partitioning — not by any field an unprivileged sender controls directly in a transaction payload to intentionally desynchronize the round mapping. [2](#0-1) 

2. **The sharded block executor is explicitly non-production / benchmark-only.** The codebase itself documents that the sharded transaction path is "only for benchmark purpose right now," and doesn't handle `AuxiliaryInfo` the way the normal unsharded (mainnet) execution path does. [3](#0-2) 

3. **Even if a mismatch occurred, this is an internal message-routing/liveness concern within the sharded executor's cross-shard synchronization, not a state-commit correctness issue that would let an unprivileged actor redirect ownership of APT, fungible assets, or objects.** A shard blocking on `Waiting` or reading stale base state would manifest as an execution correctness/liveness bug in an experimental component, not a bypass of any ownership/authority check in the Move-level custody logic (object ownership refs, FA store authority, etc.).

This falls outside the custody review bounds since it doesn't originate from unprivileged transaction/bytecode/API input crossing an actual authority check in production mainnet custody logic — it depends on internal partitioner-controlled routing metadata within a non-production sharded execution mode.

### Citations

**File:** aptos-move/aptos-vm/src/sharded_block_executor/cross_shard_client.rs (L66-86)
```rust
        let mut dependent_edges = HashMap::new();
        let mut num_dependent_edges = 0;
        for (txn_idx, txn_with_deps) in sub_block.txn_with_index_iter() {
            let mut storage_locations_to_target = HashMap::new();
            for (txn_id_with_shard, storage_locations) in txn_with_deps
                .cross_shard_dependencies
                .dependent_edges()
                .iter()
            {
                for storage_location in storage_locations {
                    storage_locations_to_target
                        .entry(storage_location.clone().into_state_key())
                        .or_insert_with(HashSet::new)
                        .insert((txn_id_with_shard.shard_id, txn_id_with_shard.round_id));
                    num_dependent_edges += 1;
                }
            }
            if !storage_locations_to_target.is_empty() {
                dependent_edges.insert(txn_idx as TxnIndex, storage_locations_to_target);
            }
        }
```

**File:** aptos-move/aptos-vm/src/sharded_block_executor/cross_shard_client.rs (L102-125)
```rust
    fn send_remote_update_for_success(&self, txn_idx: TxnIndex, txn_output: &TransactionOutput) {
        let edges = self.dependent_edges.get(&txn_idx).unwrap();

        for (state_key, write_op) in txn_output.write_set().expect_write_op_iter() {
            if let Some(dependent_shard_ids) = edges.get(state_key) {
                for (dependent_shard_id, round_id) in dependent_shard_ids.iter() {
                    trace!("Sending remote update for success for shard id {:?} and txn_idx: {:?}, state_key: {:?}, dependent shard id: {:?}", self.shard_id, txn_idx, state_key, dependent_shard_id);
                    let message = RemoteTxnWriteMsg(RemoteTxnWrite::new(
                        state_key.clone(),
                        Some(write_op.clone()),
                    ));
                    if *round_id == GLOBAL_ROUND_ID {
                        self.cross_shard_client.send_global_msg(message);
                    } else {
                        self.cross_shard_client.send_cross_shard_msg(
                            *dependent_shard_id,
                            *round_id,
                            message,
                        );
                    }
                }
            }
        }
    }
```

**File:** types/src/block_executor/partitioner.rs (L446-454)
```rust
            ExecutableTransactions::Unsharded(txns) => {
                assert!(txns.len() == auxiliary_info.len());
            },
            ExecutableTransactions::Sharded(_) => {
                // Not supporting auxiliary info here because the sharded executor is only for
                // benchmark purpose right now.
                // TODO: Revisit when we need it.
                assert!(auxiliary_info.is_empty());
            },
```
