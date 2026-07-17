### Title
Spice Epoch Endorsement Stats Accumulator Omits Last Block's Core Statement Contributions - (File: chain/chain/src/spice/core.rs)

### Summary
In the Spice protocol path, `spice_chunk_endorsement_stats_for_next_block` computes the per-epoch endorsement accumulator using only `compute_spice_endorsement_stats(prev_header.hash())`, which covers all blocks up to and including the second-to-last block of the epoch. The last block's own `SpiceCoreStatements` (which certify chunks and credit validators) are never folded into the accumulator stored in the epoch's last block header. The epoch manager reads this header field to drive validator kickout and reward decisions, so every Spice epoch's stats are systematically understated by exactly one block's worth of certified-chunk contributions.

### Finding Description
`spice_chunk_endorsement_stats_for_next_block` is called when producing the last block of a Spice epoch. It calls `compute_spice_endorsement_stats` with `prev_header.hash()`: [1](#0-0) 

`compute_spice_endorsement_stats` folds together the previous block's stored accumulator and `endorsement_contribution_of_block(prev_hash)`: [2](#0-1) 

The contribution function credits validators for every `ChunkExecutionResult` in the **credited block's** core statements: [3](#0-2) 

Because the computation is anchored at `prev_header.hash()`, the last block's own `SpiceCoreStatements` — which the block producer already has in hand at production time — are never included. The resulting `Vec<SpiceChunkEndorsementStats>` is written into the last block's header field `spice_chunk_endorsement_stats`: [4](#0-3) 

At epoch finalization, `collect_blocks_info` reads this header field to build the `spice_endorsement_tracker` that feeds directly into `compute_validators_to_reward_and_kickout`: [5](#0-4) 

The separately stored per-block accumulator (written by `record_spice_endorsement_stats_for_block` during block processing) does include the last block's contribution, but the epoch manager never reads from `DBCol::spice_endorsement_stats` for the last block — it reads only from the block header field, which was set before the last block's body was processed.

### Impact Explanation
Every Spice epoch, the endorsement contributions from the last block's certified chunks are silently dropped. Validators who endorsed chunks that happen to be certified in the last block of an epoch will have their `produced` count understated relative to their `expected` count. This directly corrupts the `ValidatorStats` fed into `compute_validators_to_reward_and_kickout`: [6](#0-5) 

and into `calculate_reward`: [7](#0-6) 

Concrete corrupted values: validator kickout decisions (`NotEnoughChunkEndorsements`), validator reward balances, and the resulting next-epoch validator set stored in `EpochInfo`.

### Likelihood Explanation
The omission is structural and fires every Spice epoch without any special triggering condition. The last block of every epoch always has core statements (certifying chunks from earlier in the epoch). Those contributions are always missed. The bug is not probabilistic — it is deterministic and epoch-wide.

### Recommendation
In `spice_chunk_endorsement_stats_for_next_block`, after computing the accumulator up to `prev_header`, additionally fold in the contribution of the last block itself using the `core_statements` that the block producer already holds at production time. The block producer has access to `core_statements` in the same code path: [8](#0-7) 

Pass the last block's `core_statements` into `spice_chunk_endorsement_stats_for_next_block` and call `endorsement_contribution_of_block` (or an equivalent) for the last block before returning the final stats. The validator path in `validate_spice_chunk_endorsement_stats` must apply the same logic to remain consistent.

### Proof of Concept
Consider a Spice epoch where the last block (height H) certifies 100 chunk slots via its core statements. `spice_chunk_endorsement_stats_for_next_block` computes `compute_spice_endorsement_stats(prev_header.hash())`, which covers heights 1…H-1 only. The 100 slots from height H are never added. If a chunk-validator-only validator was assigned to all 100 slots and endorsed them all, its `expected` count is understated by 100 and its `produced` count is understated by 100. If the validator's ratio across the rest of the epoch is near the `chunk_validator_only_kickout_threshold`, the missing 100 expected slots can push the ratio below the threshold, triggering an incorrect `NotEnoughChunkEndorsements` kickout and zero reward for that validator — a corrupted `EpochInfo` validator set and balance state. [9](#0-8)

### Citations

**File:** chain/chain/src/spice/core.rs (L373-398)
```rust
    pub fn spice_chunk_endorsement_stats_for_next_block(
        &self,
        prev_header: &BlockHeader,
        height: BlockHeight,
    ) -> Result<Vec<SpiceChunkEndorsementStats>, Error> {
        let last_final_block = prev_header.last_final_block_for_height(height);
        let is_last_block_in_epoch = self.epoch_manager.is_produced_block_last_in_epoch(
            height,
            prev_header.hash(),
            &last_final_block,
        )?;
        if !is_last_block_in_epoch {
            return Ok(Vec::new());
        }
        let epoch_id = self.epoch_manager.get_epoch_id_from_prev_block(prev_header.hash())?;
        let mut stats = compute_spice_endorsement_stats(
            &self.chain_store,
            self.epoch_manager.as_ref(),
            &epoch_id,
            prev_header.hash(),
        )?;
        if stats.iter().all(|s| *s == SpiceChunkEndorsementStats::default()) {
            stats.clear();
        }
        Ok(stats)
    }
```

**File:** chain/chain/src/spice/core.rs (L854-902)
```rust
fn endorsement_contribution_of_block(
    chain_store: &ChainStoreAdapter,
    epoch_manager: &dyn EpochManagerAdapter,
    epoch_info: &EpochInfo,
    credited_block_hash: &CryptoHash,
) -> Result<Vec<SpiceChunkEndorsementStats>, Error> {
    let credited_block = chain_store.get_block(credited_block_hash)?;
    if credited_block.header().is_genesis() || !credited_block.is_spice_block() {
        return Ok(vec![]);
    }
    let prev_uncertified =
        get_uncertified_chunks(chain_store, credited_block.header().prev_hash())?;
    let statements = credited_block.spice_core_statements();
    // (chunk, validator) -> the result they endorsed, from prior blocks and this one.
    // `unchecked_to_stored` is safe here: signatures are verified in
    // `validate_core_statements_in_block` before stats are computed.
    let endorsed_hash: HashMap<(&SpiceChunkId, &AccountId), ChunkExecutionResultHash> =
        prev_uncertified
            .iter()
            .flat_map(|info| {
                info.present_endorsements.iter().map(|(account, endorsement)| {
                    ((&info.chunk_id, account), endorsement.execution_result_hash.clone())
                })
            })
            .chain(statements.iter_endorsements().map(|endorsement| {
                (
                    (endorsement.chunk_id(), endorsement.account_id()),
                    endorsement.unchecked_to_stored().execution_result_hash,
                )
            }))
            .collect();

    let mut stats = vec![SpiceChunkEndorsementStats::default(); epoch_info.validators_iter().len()];
    for (chunk_id, execution_result) in statements.iter_execution_results() {
        let certified_hash = execution_result.compute_hash();
        let chunk_block = epoch_manager.get_block_info(&chunk_id.block_hash)?;
        let assignments = epoch_manager.get_chunk_validator_assignments(
            chunk_block.epoch_id(),
            chunk_id.shard_id,
            chunk_block.height(),
        )?;
        credit_chunk_endorsement_stats(
            &mut stats,
            assignments.assignments().iter().map(|(account_id, _stake)| account_id),
            |account_id| epoch_info.get_validator_id(account_id).copied(),
            |account_id| endorsed_hash.get(&(chunk_id, account_id)) == Some(&certified_hash),
        );
    }
    Ok(stats)
```

**File:** chain/chain/src/spice/core.rs (L950-969)
```rust
pub fn compute_spice_endorsement_stats(
    chain_store: &ChainStoreAdapter,
    epoch_manager: &dyn EpochManagerAdapter,
    epoch_id: &EpochId,
    prev_hash: &CryptoHash,
) -> Result<Vec<SpiceChunkEndorsementStats>, Error> {
    let epoch_info = epoch_manager.get_epoch_info(epoch_id)?;
    let num_validators = epoch_info.validators_iter().len();
    let contribution =
        endorsement_contribution_of_block(chain_store, epoch_manager, &epoch_info, prev_hash)?;

    // Carry the previous block's accumulator only within the same epoch; at the
    // epoch boundary (and genesis) the per-epoch accumulator resets.
    let prev_header = chain_store.get_block_header(prev_hash)?;
    let prev_stats = if !prev_header.is_genesis() && prev_header.epoch_id() == epoch_id {
        Some(get_spice_endorsement_stats(chain_store, prev_hash)?)
    } else {
        None
    };
    fold_endorsement_stats(num_validators, prev_stats.as_deref(), &contribution)
```

**File:** core/primitives/src/block_header.rs (L414-417)
```rust
    /// Per-validator chunk endorsement stats accumulated over the epoch,
    /// indexed by the current epoch's validator id. Set only on the last block
    /// of an epoch (empty otherwise); consumed by reward and kickout.
    pub spice_chunk_endorsement_stats: Vec<SpiceChunkEndorsementStats>,
```

**File:** chain/epoch-manager/src/lib.rs (L541-555)
```rust
            let chunk_validator_only =
                stats.block_stats.expected == 0 && stats.chunk_stats.expected() == 0;
            if chunk_validator_only
                && stats
                    .chunk_stats
                    .endorsement_stats()
                    .less_than(chunk_validator_only_kickout_threshold)
            {
                validator_kickout.entry(account_id.clone()).or_insert_with(|| {
                    ValidatorKickoutReason::NotEnoughChunkEndorsements {
                        produced: stats.chunk_stats.endorsement_stats().produced,
                        expected: stats.chunk_stats.endorsement_stats().expected,
                    }
                });
            }
```

**File:** chain/epoch-manager/src/lib.rs (L678-704)
```rust
        let spice_endorsement_tracker: HashMap<ValidatorId, ValidatorStats> = last_block_info
            .spice_chunk_endorsement_stats()
            .unwrap_or(&[])
            .iter()
            .enumerate()
            .map(|(validator_id, stats)| {
                (
                    validator_id as ValidatorId,
                    ValidatorStats {
                        produced: u64::from(stats.produced),
                        expected: u64::from(stats.expected),
                    },
                )
            })
            .collect();

        let config = self.config.for_protocol_version(epoch_info.protocol_version());
        // Compute kick outs for validators who are offline.
        let (validator_block_chunk_stats, kickout) = Self::compute_validators_to_reward_and_kickout(
            &config,
            &epoch_info,
            &block_validator_tracker,
            &chunk_validator_tracker,
            &spice_endorsement_tracker,
            prev_validator_kickout,
        );
        validator_kickout.extend(kickout);
```

**File:** chain/epoch-manager/src/reward_calculator.rs (L94-102)
```rust
        for (account_id, stats) in validator_block_chunk_stats {
            let production_ratio =
                get_validator_online_ratio(&stats, online_thresholds.endorsement_cutoff_threshold);
            let average_produced_numer = production_ratio.numer();
            let average_produced_denom = production_ratio.denom();

            let expected_blocks = stats.block_stats.expected;
            let expected_chunks = stats.chunk_stats.expected();
            let expected_endorsements = stats.chunk_stats.endorsement_stats().expected;
```

**File:** chain/client/src/client.rs (L1141-1165)
```rust
        let spice_info = if ProtocolFeature::Spice.enabled(protocol_version) {
            let core_statements = SpiceCoreStatements::new(
                self.chain.spice_core_reader.core_statements_for_next_block(&prev_header)?,
            );
            let newly_certified_block_execution_results = self
                .chain
                .spice_core_reader
                .get_newly_certified_block_execution_results_for_next_block(
                    prev_header,
                    &core_statements,
                )?;
            let prev_last_certified_block_epoch_id = self
                .chain
                .spice_core_reader
                .prev_last_certified_block_epoch_id(prev_header.hash())?;
            let spice_chunk_endorsement_stats = self
                .chain
                .spice_core_reader
                .spice_chunk_endorsement_stats_for_next_block(prev_header, height)?;
            Some(SpiceNewBlockProductionInfo {
                core_statements,
                newly_certified_block_execution_results,
                prev_last_certified_block_epoch_id,
                spice_chunk_endorsement_stats,
            })
```
