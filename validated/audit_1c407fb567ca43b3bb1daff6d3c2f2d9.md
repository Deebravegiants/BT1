### Title
Unvalidated `builder` (Sequencer Address) in `ProposalInit` Allows Any Proposer to Redirect Fees and Corrupt Block Hash — (File: `crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

### Summary

The `builder` field of `ProposalInit` is proposer-supplied and flows directly into `sequencer_address` inside `BlockInfo` used for block execution. The validator's `is_proposal_init_valid` function never checks `builder` against any locally-trusted reference. Any validator who holds the proposer role for a round can set `builder` to an arbitrary address; all other validators will accept the proposal, execute every transaction in the block with the wrong sequencer address (redirecting fees), and commit a block whose hash permanently encodes the wrong sequencer address.

### Finding Description

`is_proposal_init_valid` in `validate_proposal.rs` validates `height`, `l1_da_mode`, `l2_gas_price_fri`, `timestamp`, `starknet_version`, `version_constant_commitment`, all four L1 gas price fields, and `fee_proposal_fri`. The `builder` field is absent from `ProposalInitValidation` and is never checked. [1](#0-0) 

The full set of validated fields in `is_proposal_init_valid`: [2](#0-1) 

`builder` is not among them. Immediately after validation, `convert_to_sn_api_block_info` maps `init.builder` directly to `sequencer_address`: [3](#0-2) 

`sequencer_address` is then stored in `PartialBlockHashComponents.sequencer` and hashed into the block hash: [4](#0-3) [5](#0-4) 

Because both the proposer and every validator derive `sequencer_address` from the same `init.builder` wire value, both sides compute the identical `partial_block_hash`. The `ProposalFinMismatch` guard therefore passes unconditionally regardless of what `builder` contains: [6](#0-5) 

The block is committed with the attacker-chosen sequencer address.

### Impact Explanation

**Wrong fee destination (economic impact).** In Starknet, transaction fees are transferred to `sequencer_address`. Every fee paid in the manipulated block is redirected to the attacker-controlled address instead of the legitimate sequencer.

**Wrong `get_sequencer_address` syscall result.** Any contract that calls `get_sequencer_address` during that block receives the attacker's address. Access-control logic, fee-sharing contracts, or any protocol that gates on the sequencer address will behave incorrectly.

**Permanently wrong block hash.** `sequencer_address` is a direct input to `calculate_block_hash`. The committed block hash encodes the wrong sequencer, corrupting the canonical chain state for all downstream consumers (provers, bridges, RPC clients). [7](#0-6) 

### Likelihood Explanation

Every validator takes the proposer role in rotation. No special privilege beyond holding a validator key is required. The attack is silent — no anomalous error is logged, no metric fires, and the `ProposalFinMismatch` check passes. The production deployment config already ships `compare_retrospective_block_hash: false`, confirming that the cross-check path is intentionally relaxed in production, making the absence of a `builder` check even more consequential. [8](#0-7) 

### Recommendation

Add `builder_address: ContractAddress` to `ProposalInitValidation` and enforce it in `is_proposal_init_valid`:

```rust
if init_proposed.builder != proposal_init_validation.builder_address {
    return Err(ValidateProposalError::InvalidProposalInit(
        init_proposed.clone(),
        proposal_init_validation.clone(),
        format!(
            "builder mismatch: expected={:?}, proposed={:?}",
            proposal_init_validation.builder_address, init_proposed.builder
        ),
    ));
}
```

Populate `builder_address` from `self.config.static_config.builder_address` at the two call sites in `sequencer_consensus_context.rs` where `ProposalInitValidation` is constructed. [9](#0-8) 

### Proof of Concept

1. A malicious validator waits for their proposer turn at height H.
2. In `initiate_build`, they override `builder` in the constructed `ProposalInit` to their own wallet address `0xATTACKER`.
3. The `ProposalInit` is broadcast to all validators.
4. Each validator calls `validate_proposal` → `is_proposal_init_valid`: `builder` is not in `ProposalInitValidation`, check is skipped.
5. Each validator calls `initiate_validation` → `convert_to_sn_api_block_info(init)`: `sequencer_address = 0xATTACKER`.
6. The batcher executes all transactions with `sequencer_address = 0xATTACKER`; all fees are transferred to `0xATTACKER`.
7. `BlockExecutionArtifacts::new` builds `PartialBlockHashComponents` with `sequencer = 0xATTACKER`.
8. Both proposer and validator compute the same `partial_block_hash` (both used `init.builder`).
9. `ProposalFinMismatch` check passes; `validate_proposal` returns `Ok(built_block)`.
10. Consensus reaches decision; `decision_reached` commits the block with `sequencer_address = 0xATTACKER` and a block hash that permanently encodes the attacker's address. [10](#0-9) [11](#0-10)

### Citations

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L73-85)
```rust
// Contains parameters required for validating ProposalInit.
#[derive(Clone, Debug)]
pub(crate) struct ProposalInitValidation {
    pub height: BlockNumber,
    pub block_timestamp_window_seconds: u64,
    pub previous_proposal_init: Option<PreviousProposalInitInfo>,
    pub l1_da_mode: L1DataAvailabilityMode,
    pub l2_gas_price_fri: GasPrice,
    pub starknet_version: StarknetVersion,
    /// fee_actual from the sliding window. `None` until the window has accumulated
    /// `fee_proposal_window_size` entries (startup / near-genesis).
    pub fee_actual: Option<GasPrice>,
}
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L243-247)
```rust
    // TODO(matan): Switch to signature validation.
    if built_block != received_fin.proposal_commitment {
        CONSENSUS_PROPOSAL_FIN_MISMATCH.increment(1);
        return Err(ValidateProposalError::ProposalFinMismatch);
    }
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L312-321)
```rust
    if !(init_proposed.height == proposal_init_validation.height
        && init_proposed.l1_da_mode == proposal_init_validation.l1_da_mode
        && init_proposed.l2_gas_price_fri == proposal_init_validation.l2_gas_price_fri)
    {
        return Err(ValidateProposalError::InvalidProposalInit(
            init_proposed.clone(),
            proposal_init_validation.clone(),
            "ProposalInit validation failed".to_string(),
        ));
    }
```

**File:** crates/apollo_consensus_orchestrator/src/utils.rs (L329-347)
```rust
    Ok(starknet_api::block::BlockInfo {
        block_number: init.height,
        block_timestamp: BlockTimestamp(init.timestamp),
        sequencer_address: init.builder,
        gas_prices: GasPrices {
            strk_gas_prices: GasPriceVector {
                l1_gas_price: l1_gas_price_fri,
                l1_data_gas_price: l1_data_gas_price_fri,
                l2_gas_price: l2_gas_price_fri,
            },
            eth_gas_prices: GasPriceVector {
                l1_gas_price: l1_gas_price_wei,
                l1_data_gas_price: l1_data_gas_price_wei,
                l2_gas_price: l2_gas_price_wei,
            },
        },
        use_kzg_da: init.l1_da_mode.is_use_kzg_da(),
        starknet_version: init.starknet_version,
    })
```

**File:** crates/starknet_api/src/block_hash/block_hash_calculator.rs (L223-235)
```rust
impl PartialBlockHashComponents {
    pub fn new(block_info: &BlockInfo, header_commitments: BlockHeaderCommitments) -> Self {
        Self {
            header_commitments,
            block_number: block_info.block_number,
            l1_gas_price: block_info.gas_prices.l1_gas_price_per_token(),
            l1_data_gas_price: block_info.gas_prices.l1_data_gas_price_per_token(),
            l2_gas_price: block_info.gas_prices.l2_gas_price_per_token(),
            sequencer: SequencerContractAddress(block_info.sequencer_address),
            timestamp: block_info.block_timestamp,
            starknet_version: block_info.starknet_version,
        }
    }
```

**File:** crates/starknet_api/src/block_hash/block_hash_calculator.rs (L245-282)
```rust
pub fn calculate_block_hash(
    partial_block_hash_components: &PartialBlockHashComponents,
    state_root: GlobalRoot,
    previous_block_hash: BlockHash,
) -> StarknetApiResult<BlockHash> {
    let block_hash_version: BlockHashVersion =
        partial_block_hash_components.starknet_version.try_into()?;
    let block_commitments = &partial_block_hash_components.header_commitments;
    Ok(BlockHash(
        HashChain::new()
            .chain(&block_hash_version.clone().into())
            .chain(&partial_block_hash_components.block_number.0.into())
            .chain(&state_root.0)
            .chain(&partial_block_hash_components.sequencer.0)
            .chain(&partial_block_hash_components.timestamp.0.into())
            .chain(&block_commitments.concatenated_counts)
            .chain(&block_commitments.state_diff_commitment.0.0)
            .chain(&block_commitments.transaction_commitment.0)
            .chain(&block_commitments.event_commitment.0)
            .chain(&block_commitments.receipt_commitment.0)
            .chain_iter(
                gas_prices_to_hash(
                    &partial_block_hash_components.l1_gas_price,
                    &partial_block_hash_components.l1_data_gas_price,
                    &partial_block_hash_components.l2_gas_price,
                    &block_hash_version,
                )
                .iter(),
            )
            .chain(
                &Felt::try_from(&partial_block_hash_components.starknet_version)
                    .expect("Expect ASCII version"),
            )
            .chain(&Felt::ZERO)
            .chain(&previous_block_hash.0)
            .get_poseidon_hash(),
    ))
}
```

**File:** crates/apollo_deployments/resources/app_configs/consensus_manager_config.json (L60-60)
```json
  "consensus_manager_config.context_config.dynamic_config.compare_retrospective_block_hash": false,
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L879-900)
```rust
            std::cmp::Ordering::Equal => {
                let proposal_init_validation = ProposalInitValidation {
                    height: init.height,
                    block_timestamp_window_seconds: self
                        .config
                        .static_config
                        .block_timestamp_window_seconds,
                    previous_proposal_init: self.previous_proposal_init.clone(),
                    l1_da_mode: self.l1_da_mode,
                    l2_gas_price_fri: self
                        .config
                        .dynamic_config
                        .override_l2_gas_price_fri
                        .map(GasPrice)
                        .unwrap_or(self.l2_gas_price),
                    starknet_version: StarknetVersion::LATEST,
                    fee_actual: compute_fee_actual(
                        &self.fee_proposals_window,
                        init.height,
                        VersionedConstants::latest_constants().fee_proposal_window_size,
                    ),
                };
```

**File:** crates/apollo_batcher/src/block_builder.rs (L147-195)
```rust
impl BlockExecutionArtifacts {
    pub async fn new(
        block_summary: BlockExecutionSummary,
        execution_data: BlockTransactionExecutionData,
        final_n_executed_txs: usize,
    ) -> Self {
        #[cfg(feature = "os_input")]
        let initial_reads = block_summary.initial_reads;
        let BlockExecutionSummary {
            state_diff: commitment_state_diff,
            compressed_state_diff,
            bouncer_weights,
            casm_hash_computation_data_sierra_gas,
            casm_hash_computation_data_proving_gas,
            compiled_class_hashes_for_migration,
            block_info,
            // TODO(Yoav): Remove the ".." when the os_input feature is removed.
            ..
        } = block_summary;
        let l1_da_mode = L1DataAvailabilityMode::from_use_kzg_da(block_info.use_kzg_da);
        let transactions_data =
            prepare_txs_hashing_data(&execution_data.execution_infos_and_signatures);
        // TODO(Ayelet): Remove the clones.
        let (header_commitments, measurements) = calculate_block_commitments(
            &transactions_data,
            ThinStateDiff::from(commitment_state_diff.clone()),
            l1_da_mode,
            &block_info.starknet_version,
        )
        .await;
        record_and_log_block_commitment_measurements(block_info.block_number, measurements);
        let partial_block_hash_components =
            PartialBlockHashComponents::new(&block_info, header_commitments);
        let l2_gas_used = execution_data.l2_gas_used();
        Self {
            execution_data,
            commitment_state_diff,
            compressed_state_diff,
            #[cfg(feature = "os_input")]
            initial_reads,
            bouncer_weights,
            l2_gas_used,
            casm_hash_computation_data_sierra_gas,
            casm_hash_computation_data_proving_gas,
            compiled_class_hashes_for_migration,
            final_n_executed_txs,
            partial_block_hash_components,
        }
    }
```

**File:** crates/apollo_batcher/src/block_builder.rs (L215-222)
```rust
    pub fn commitment(&self) -> ProposalCommitment {
        ProposalCommitment {
            partial_block_hash: PartialBlockHash::from_partial_block_hash_components(
                &self.partial_block_hash_components,
            )
            .expect("Unable to calculate the proposal commitment"),
        }
    }
```
