Based on the code, the claimed quadratic-cost vulnerability does not hold up.

`check_merkle_root_consistency` performs a single `HashMap` lookup/comparison against the `merkle_root_meta` for that specific `erasure_set` — O(1) per shred [1](#0-0) . It's invoked once per data shred in `check_insert_data_shred` and once per coding shred in `check_insert_coding_shred`, each keyed by `(location, erasure_set)` in the `merkle_root_metas` map [2](#0-1) [3](#0-2) [4](#0-3) . `check_chained_merkle_root_consistency` (the SIMD-0340 forward/backward FEC-chaining check) also iterates the `merkle_root_metas` map exactly once, doing O(1) hashmap lookups per FEC set for the forward and backward checks [5](#0-4) . There is no nested loop over all erasure sets or all previously seen shreds — total work across a shred-insertion batch is linear in the number of shreds/FEC sets, not quadratic.

Because FEC-set count is a direct function of the number of shreds, which is itself a function of serialized transaction/entry byte volume (each FEC set covers a fixed number of ~1203-byte data shreds), inflating FEC-set count requires inflating total block data volume. That data volume is already reflected in the cost model via `data_bytes_cost` (`get_instructions_data_cost`) and other components summed in `TransactionCost` [6](#0-5) [7](#0-6) . "Instruction/account diversity" alone (without increasing byte volume) does not increase the number of shreds or FEC sets, since shredding depends on entry-serialized size, not the semantic diversity of instructions/accounts within it. So the premised mechanism — attacker maximizing instruction/account diversity to inflate FEC-set count independent of costed data volume — has no support in the shredding or insertion code, and the insertion-side duplicate/merkle checks are linear (O(1) per shred/FEC set), not quadratic.

No vulnerability found for this question.

### Citations

**File:** ledger/src/blockstore.rs (L1834-1889)
```rust
        for ((location, erasure_set), working_merkle_root_meta) in
            shred_insertion_tracker.merkle_root_metas.iter()
        {
            if !working_merkle_root_meta.should_write() {
                // Not a new merkle root meta
                continue;
            }
            let (slot, _) = erasure_set.store_key();

            // Note: this check is not performed on Alternate columns as they are already validated
            // via a separate merkle proof on repair ingest
            if !matches!(location, BlockLocation::Original) {
                continue;
            }

            let merkle_root_meta = working_merkle_root_meta.as_ref();
            let shred_id = ShredId::new(
                slot,
                merkle_root_meta.first_received_shred_index(),
                merkle_root_meta.first_received_shred_type(),
            );
            let shred = shred_insertion_tracker
                .just_inserted_shreds
                .get(&(*location, shred_id))
                .expect("Merkle root meta was just created, initial shred must exist");

            // Forward check for SIMD-0340
            if let Some(next_erasure_set) = erasure_set.next_fec_set()
                && !self.check_forward_chained_merkle_root_consistency(
                    shred,
                    next_erasure_set,
                    &shred_insertion_tracker.just_inserted_shreds,
                    &shred_insertion_tracker.merkle_root_metas,
                )
            {
                shred_insertion_tracker.duplicate_shreds.push(
                    PossibleDuplicateShred::FixedFECChainedMerkleRootConflict(slot),
                );
                continue;
            }

            // Backwards check for SIMD-0340
            if let Some(prev_shred_id) = self
                .previous_fec_set_shred_id(erasure_set, &shred_insertion_tracker.merkle_root_metas)
                && !self.check_backwards_chained_merkle_root_consistency(
                    shred,
                    prev_shred_id,
                    &shred_insertion_tracker.just_inserted_shreds,
                )
            {
                shred_insertion_tracker.duplicate_shreds.push(
                    PossibleDuplicateShred::FixedFECChainedMerkleRootConflict(slot),
                );
                continue;
            }
        }
```

**File:** ledger/src/blockstore.rs (L2617-2622)
```rust
        if let HashMapEntry::Vacant(entry) =
            merkle_root_metas.entry((BlockLocation::Original, erasure_set))
            && let Some(meta) = self.merkle_root_meta(erasure_set).unwrap()
        {
            entry.insert(WorkingEntry::Clean(meta));
        }
```

**File:** ledger/src/blockstore.rs (L2843-2849)
```rust
        if let HashMapEntry::Vacant(entry) = merkle_root_metas.entry((location, erasure_set))
            && let Some(meta) = self
                .merkle_root_meta_from_location(erasure_set, location)
                .unwrap()
        {
            entry.insert(WorkingEntry::Clean(meta));
        }
```

**File:** ledger/src/blockstore.rs (L2886-2897)
```rust
            if let Some(merkle_root_meta) = merkle_root_metas.get(&(location, erasure_set)) {
                // A previous shred has been inserted in this batch or in blockstore
                // Compare our current shred against the previous shred for potential
                // conflicts
                if !self.check_merkle_root_consistency(
                    just_inserted_shreds,
                    slot,
                    location,
                    merkle_root_meta.as_ref(),
                    &shred,
                    duplicate_shreds,
                ) {
```

**File:** ledger/src/blockstore.rs (L3023-3037)
```rust
    fn check_merkle_root_consistency(
        &self,
        just_inserted_shreds: &HashMap<(BlockLocation, ShredId), Cow<'_, Shred>>,
        slot: Slot,
        location: BlockLocation,
        merkle_root_meta: &MerkleRootMeta,
        shred: &Shred,
        duplicate_shreds: &mut Vec<PossibleDuplicateShred>,
    ) -> bool {
        let new_merkle_root = shred.merkle_root().ok();
        if merkle_root_meta.merkle_root() == new_merkle_root {
            // No conflict, either both merkle shreds with same merkle root
            // or both legacy shreds with merkle_root `None`
            return true;
        }
```

**File:** cost-model/src/cost_model.rs (L103-127)
```rust
    fn calculate_transaction_cost<'a, Tx: TransactionMeta>(
        transaction: &'a Tx,
        instructions: impl Iterator<Item = (&'a Pubkey, SVMInstruction<'a>)>,
        num_write_locks: u64,
        programs_execution_cost: u64,
        loaded_accounts_data_size_cost: u64,
        data_bytes_cost: u16,
        feature_set: &FeatureSet,
    ) -> TransactionCost<'a, Tx> {
        let signature_cost = Self::get_signature_cost(transaction);
        let write_lock_cost = Self::get_write_lock_cost(num_write_locks);

        let allocated_accounts_data_size =
            Self::calculate_allocated_accounts_data_size(instructions, feature_set);

        TransactionCost {
            transaction,
            signature_cost,
            write_lock_cost,
            data_bytes_cost,
            programs_execution_cost,
            loaded_accounts_data_size_cost,
            allocated_accounts_data_size,
        }
    }
```

**File:** cost-model/src/cost_model.rs (L180-183)
```rust
    /// Return the instruction data bytes cost.
    fn get_instructions_data_cost(transaction: &impl TransactionMeta) -> u16 {
        transaction.instruction_data_len() / (INSTRUCTION_DATA_BYTES_COST as u16)
    }
```
