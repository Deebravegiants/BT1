No vulnerability found for this question.

**Reasoning:** The `CrossShardCommitSender`/`CrossShardCommitReceiver` and `RemoteTxnWrite` mechanism in [1](#0-0)  is purely an internal, in-process communication channel used by the sharded block executor while executing a single block that has already been partitioned and agreed upon. The `write_op` values sent in a `RemoteTxnWriteMsg` are derived directly from `txn_output.write_set()` — the actual execution output of the source transaction that owns the dependent edge [2](#0-1) , not from any externally supplied or attacker-controlled data structure. The `dependent_edges` map is constructed from the block partitioner's static dependency analysis of the sub-block [3](#0-2) , and the `CrossShardClient` trait implementations are internal channels between local shard-executor threads/processes, not a network-exposed or unprivileged-transaction-reachable API [4](#0-3) .

There is no code path by which an unprivileged transaction, package, view, authenticator, API, bytecode, or proof input can construct or inject an arbitrary `RemoteTxnWrite` message into this channel. Crafting such a message would require compromising the executor process/thread itself (i.e., malicious node/peer behavior), which is explicitly excluded by the review bounds ("Ignore malicious peer or node behavior"). Since there is no unprivileged entrypoint feeding attacker-controlled data into `send_remote_update_for_success`, the described scenario does not cross a real custody boundary from unprivileged input as required by the decision standard.

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

**File:** aptos-move/aptos-vm/src/sharded_block_executor/cross_shard_client.rs (L139-145)
```rust
pub trait CrossShardClient: Send + Sync {
    fn send_global_msg(&self, msg: CrossShardMsg);

    fn send_cross_shard_msg(&self, shard_id: ShardId, round: RoundId, msg: CrossShardMsg);

    fn receive_cross_shard_msg(&self, current_round: RoundId) -> CrossShardMsg;
}
```
