### Title
Unvalidated `builder` Field in `ProposalInit` Allows Malicious Proposer to Inject Arbitrary `sequencer_address` into Block Hash and Execution Context — (`File: crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

### Summary

`is_proposal_init_valid` validates many fields of a received `ProposalInit` (height, l1_da_mode, l2_gas_price_fri, all four L1 gas prices, starknet_version, version_constant_commitment, fee_proposal_fri, timestamp) but never checks the `builder` field. `builder` is the only field that `convert_to_sn_api_block_info` maps to `sequencer_address` in `BlockInfo`, which is then committed into `PartialBlockHashComponents` and hashed into the final block hash. A malicious proposer can set `builder` to any arbitrary `ContractAddress`, causing every validator to execute the block and compute the block hash with an attacker-controlled sequencer address, producing a wrong committed block hash and wrong execution results for any contract that calls `get_sequencer_address`.

### Finding Description

`ProposalInit.builder` is defined as "Address of the one who builds/sequences the block." During proposal validation, `is_proposal_init_valid` is called first and checks the following fields against locally-derived reference values:

- `height`, `l1_da_mode`, `l2_gas_price_fri` (exact match)
- `starknet_version`, `version_constant_commitment` (exact match)
- `l1_gas_price_fri`, `l1_data_gas_price_fri`, `l1_gas_price_wei`, `l1_data_gas_price_wei` (within margin)
- `timestamp` (window check)
- `fee_proposal_fri` (bounds check)

`builder` is **not checked at all**. After `is_proposal_init_valid` returns `Ok`, `initiate_validation` calls `convert_to_sn_api_block_info(init)`:

```rust
// crates/apollo_consensus_orchestrator/src/utils.rs:329-347
Ok(starknet_api::block::BlockInfo {
    block_number: init.height,
    block_timestamp: BlockTimestamp(init.timestamp),
    sequencer_address: init.builder,   // ← attacker-controlled
    gas_prices: GasPrices { ... },
    use_kzg_da: init.l1_da_mode.is_use_kzg_da(),
    starknet_version: init.starknet_version,
})
```

This `BlockInfo` is passed to the batcher's `validate_block`, which executes all transactions with `sequencer_address = init.builder`. After execution, `BlockExecutionArtifacts::new` calls `PartialBlockHashComponents::new(&block_info, header_commitments)`:

```rust
// crates/starknet_api/src/block_hash/block_hash_calculator.rs:224-235
pub fn new(block_info: &BlockInfo, header_commitments: BlockHeaderCommitments) -> Self {
    Self {
        ...
        sequencer: SequencerContractAddress(block_info.sequencer_address),  // ← attacker-controlled
        ...
    }
}
```

And `calculate_block_hash` chains `sequencer` into the Poseidon hash:

```rust
// crates/starknet_api/src/block_hash/block_hash_calculator.rs:258
.chain(&partial_block_hash_components.sequencer.0)
```

Because the validator uses the proposer-supplied `builder` without checking it, the validator's locally-computed `batcher_block_commitment` will match the proposer's `ProposalFin.proposal_commitment` (both computed with the same attacker-chosen address). The final check `built_block != received_fin.proposal_commitment` passes, and the block is accepted.

### Impact Explanation

1. **Wrong block hash committed to L1**: The `sequencer_address` is a direct input to `calculate_block_hash`. An attacker-controlled `builder` produces a block hash that encodes the wrong sequencer identity. This hash is stored in state and eventually anchored to L1.

2. **Wrong execution results**: Any contract that calls the `get_sequencer_address` syscall during execution will receive the attacker-supplied address instead of the legitimate sequencer address. This corrupts execution results, receipts, and events for those contracts.

3. **Wrong fee collection**: Sequencer fees are directed to `sequencer_address`. Setting `builder` to an attacker-controlled address redirects fee revenue.

All validators accept the block because they all derive `sequencer_address` from the unvalidated `builder` field, so the commitment comparison succeeds.

### Likelihood Explanation

Any consensus participant whose turn it is to propose a block can trigger this. No privileged access is required — the proposer simply sets `builder` to an arbitrary `ContractAddress` in the `ProposalInit` message it broadcasts. The attack is a single-message, zero-cost operation executable by any node in the validator set.

### Recommendation

Add `builder` to `ProposalInitValidation` and enforce it in `is_proposal_init_valid`. The validator node has a locally-configured `builder_address` (set in `ContextConfig.static_config.builder_address` and used by the proposer in `initiate_build`). The validator should reject any `ProposalInit` whose `builder` does not match the expected sequencer address:

```rust
// In ProposalInitValidation, add:
pub builder: ContractAddress,

// In is_proposal_init_valid, add:
if init_proposed.builder != proposal_init_validation.builder {
    return Err(ValidateProposalError::InvalidProposalInit(
        init_proposed.clone(),
        proposal_init_validation.clone(),
        format!("builder mismatch: expected={:?}, proposed={:?}",
            proposal_init_validation.builder, init_proposed.builder),
    ));
}
```

### Proof of Concept

1. Attacker is the current round's proposer.
2. Attacker constructs `ProposalInit` with `builder = ContractAddress::from(0xdeadbeef)` (any arbitrary address).
3. Attacker builds the block normally; the batcher executes transactions with `sequencer_address = 0xdeadbeef`.
4. Attacker sends `ProposalFin` with the commitment derived from that execution.
5. Each validator receives the `ProposalInit`, calls `is_proposal_init_valid` — passes (no `builder` check).
6. Each validator calls `convert_to_sn_api_block_info(init)` → `sequencer_address = 0xdeadbeef`.
7. Each validator's batcher executes with `sequencer_address = 0xdeadbeef`, computes the same block hash.
8. `built_block == received_fin.proposal_commitment` → block accepted.
9. Block with `sequencer_address = 0xdeadbeef` is committed to state and eventually to L1.

**Corrupted value**: `PartialBlockHashComponents.sequencer` = attacker-chosen address → wrong `BlockHash` stored in state and committed to L1; wrong return value for `get_sequencer_address` syscall in all transactions in that block. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6)

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

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L252-321)
```rust
#[instrument(level = "warn", skip_all, fields(?proposal_init_validation, ?init_proposed))]
async fn is_proposal_init_valid(
    proposal_init_validation: &ProposalInitValidation,
    init_proposed: &ProposalInit,
    clock: &dyn Clock,
    l1_gas_price_provider: Arc<dyn L1GasPriceProviderClient>,
    gas_price_params: &GasPriceParams,
) -> ValidateProposalResult<()> {
    let now: u64 = clock.unix_now();
    let last_block_timestamp =
        proposal_init_validation.previous_proposal_init.as_ref().map_or(0, |info| info.timestamp);
    if init_proposed.timestamp < last_block_timestamp {
        return Err(ValidateProposalError::InvalidProposalInit(
            init_proposed.clone(),
            proposal_init_validation.clone(),
            format!(
                "Timestamp is too old: last_block_timestamp={}, proposed={}",
                last_block_timestamp, init_proposed.timestamp
            ),
        ));
    }
    if init_proposed.timestamp > now + proposal_init_validation.block_timestamp_window_seconds {
        return Err(ValidateProposalError::InvalidProposalInit(
            init_proposed.clone(),
            proposal_init_validation.clone(),
            format!(
                "Timestamp is in the future: now={}, block_timestamp_window_seconds={}, \
                 proposed={}",
                now,
                proposal_init_validation.block_timestamp_window_seconds,
                init_proposed.timestamp
            ),
        ));
    }
    if init_proposed.starknet_version != proposal_init_validation.starknet_version {
        return Err(ValidateProposalError::InvalidProposalInit(
            init_proposed.clone(),
            proposal_init_validation.clone(),
            format!(
                "starknet_version mismatch: expected={:?}, proposed={:?}",
                proposal_init_validation.starknet_version, init_proposed.starknet_version
            ),
        ));
    }
    // `version_constant_commitment` is proposer-supplied (network-derived). It is not yet a real
    // commitment (see `expected_version_constant_commitment`): the only valid value is the
    // sentinel, so reject anything else. Enforcing the same value the proposer emits keeps the two
    // sides in lockstep, so a real value cannot ship on one side without the other.
    let expected_commitment = expected_version_constant_commitment();
    if init_proposed.version_constant_commitment != expected_commitment {
        return Err(ValidateProposalError::InvalidProposalInit(
            init_proposed.clone(),
            proposal_init_validation.clone(),
            format!(
                "version_constant_commitment mismatch: expected={expected_commitment:?}, \
                 proposed={:?}",
                init_proposed.version_constant_commitment
            ),
        ));
    }
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

**File:** crates/apollo_consensus_orchestrator/src/utils.rs (L301-347)
```rust
pub(crate) fn convert_to_sn_api_block_info(
    init: &ProposalInit,
) -> Result<starknet_api::block::BlockInfo, StarknetApiError> {
    if init.l1_gas_price_fri.0 == 0
        || init.l1_gas_price_wei.0 == 0
        || init.l1_data_gas_price_fri.0 == 0
        || init.l1_data_gas_price_wei.0 == 0
        || init.l2_gas_price_fri.0 == 0
    {
        warn!("Zero gas price detected in block info: {:?}", init);
    }

    let l1_gas_price_fri = NonzeroGasPrice::new(init.l1_gas_price_fri)?;
    let l1_data_gas_price_fri = NonzeroGasPrice::new(init.l1_data_gas_price_fri)?;
    let l1_gas_price_wei = NonzeroGasPrice::new(init.l1_gas_price_wei)?;
    let l1_data_gas_price_wei = NonzeroGasPrice::new(init.l1_data_gas_price_wei)?;
    let l2_gas_price_fri = NonzeroGasPrice::new(init.l2_gas_price_fri)?;
    let proposal_init_info = PreviousProposalInitInfo::from(init);
    let eth_to_fri_rate = calculate_eth_to_fri_rate(&proposal_init_info)?;

    let l2_gas_price_wei = NonzeroGasPrice::new(init.l2_gas_price_fri.fri_to_wei(eth_to_fri_rate)?)
        .inspect_err(|_| {
            warn!(
                "L2 gas price in wei is zero! Conversion rate: {eth_to_fri_rate}, L2 gas price in \
                 FRI: {}",
                init.l2_gas_price_fri
            )
        })?;
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

**File:** crates/starknet_api/src/block_hash/block_hash_calculator.rs (L253-281)
```rust
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
```

**File:** crates/apollo_protobuf/src/consensus.rs (L95-128)
```rust
pub struct ProposalInit {
    /// The height of the consensus (block number).
    pub height: BlockNumber,
    /// The current round of the consensus.
    pub round: Round,
    /// The last round that was valid.
    pub valid_round: Option<Round>,
    /// Address of the one who proposed the block in consensus.
    pub proposer: ContractAddress,
    /// Block timestamp.
    pub timestamp: u64,
    /// Address of the one who builds/sequences the block.
    pub builder: ContractAddress,
    /// L1 data availability mode.
    pub l1_da_mode: L1DataAvailabilityMode,
    /// L2 gas price in FRI.
    pub l2_gas_price_fri: GasPrice,
    /// L1 gas price in FRI.
    pub l1_gas_price_fri: GasPrice,
    /// L1 data gas price in FRI.
    pub l1_data_gas_price_fri: GasPrice,
    // Keeping the wei prices for now, to use with L1 transactions.
    /// L1 gas price in WEI.
    pub l1_gas_price_wei: GasPrice,
    /// L1 data gas price in WEI.
    pub l1_data_gas_price_wei: GasPrice,
    /// Starknet protocol version.
    pub starknet_version: starknet_api::block::StarknetVersion,
    /// Version constant commitment.
    pub version_constant_commitment: StarkHash,
    /// Proposer's oracle-derived recommended L2 gas fee. Present iff
    /// `starknet_version >= V0_14_3`.
    pub fee_proposal_fri: Option<GasPrice>,
}
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
