### Title
Unvalidated `ProposalInit.builder` Field Allows Malicious Proposer to Redirect Sequencer Fees and Corrupt Block Hash — (`File: crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

### Summary

`is_proposal_init_valid` validates many `ProposalInit` fields (timestamp, `starknet_version`, `l1_da_mode`, `l2_gas_price_fri`, all four L1 gas prices, `fee_proposal_fri`) but never checks the `builder` field. The `builder` address is consumed verbatim as the `sequencer_address` in `BlockInfo`, in `PartialBlockHashComponents`, and in the `BlockHeaderWithoutHash` written to state sync. A malicious-but-legitimately-selected proposer can set `builder` to any address; every validator will re-execute the block with that address and produce the same `ProposalCommitment`, so the proposal passes the fin-mismatch check and is committed.

### Finding Description

`is_proposal_init_valid` in `validate_proposal.rs` checks the following `ProposalInit` fields: [1](#0-0) 

`builder` is absent from every check. After validation passes, `initiate_validation` calls `convert_to_sn_api_block_info(init)`, which maps `init.builder` directly to `sequencer_address`: [2](#0-1) 

That `BlockInfo` is forwarded to the batcher as `ValidateBlockInput.block_info`: [3](#0-2) 

The same `init.builder` is also written into `PartialBlockHashComponents.sequencer` (via `BlockExecutionArtifacts::new` → `PartialBlockHashComponents::new`), which feeds `PartialBlockHash::from_partial_block_hash_components` and therefore the `ProposalCommitment`: [4](#0-3) [5](#0-4) 

And into the `BlockHeaderWithoutHash` sent to state sync: [6](#0-5) 

The proposer sets `builder` from a static config field with a TODO noting it should eventually come from the committee: [7](#0-6) 

Because both proposer and validator derive the `PartialBlockHash` from the same (unvalidated) `init.builder`, the fin-mismatch check always passes regardless of what `builder` contains: [8](#0-7) 

### Impact Explanation

1. **Wrong fee recipient / economic theft.** The blockifier uses `BlockInfo.sequencer_address` as the fee-collection address. Every transaction fee in the block is transferred to `init.builder`. A malicious proposer sets `builder` to an attacker-controlled address and collects all fees for that block.

2. **Wrong `get_sequencer_address` syscall result.** Contracts that call the `get_sequencer_address` syscall receive the attacker-supplied address, producing wrong execution results for any contract logic that depends on the sequencer identity.

3. **Wrong block hash committed to state.** `PartialBlockHashComponents.sequencer` is hashed into the block hash. The committed block hash diverges from what an honest node would compute for the same transactions, corrupting the authoritative chain state.

4. **Wrong block header in state sync.** `BlockHeaderWithoutHash.sequencer` is stored with the attacker's address, poisoning the RPC view of the block header.

### Likelihood Explanation

Any validator that is legitimately selected as proposer for a round can trigger this. Tendermint rotates proposers deterministically by stake weight, so every validator eventually proposes. No special privilege beyond being a committee member is required. The attack is a single-field substitution in `ProposalInit` with no cryptographic barrier.

### Recommendation

Add a `builder` check inside `is_proposal_init_valid`. Until the committee-derived builder address is available, validate that `init.builder` equals the locally configured `builder_address` (the same value the honest proposer would emit):

```rust
if init_proposed.builder != proposal_init_validation.expected_builder {
    return Err(ValidateProposalError::InvalidProposalInit(
        init_proposed.clone(),
        proposal_init_validation.clone(),
        format!("builder mismatch: expected={:?}, proposed={:?}",
            proposal_init_validation.expected_builder, init_proposed.builder),
    ));
}
```

Add `expected_builder: ContractAddress` to `ProposalInitValidation` and populate it from `self.config.static_config.builder_address` at the two call sites in `sequencer_consensus_context.rs`. [9](#0-8) 

### Proof of Concept

1. A malicious validator is selected as proposer for height H, round R.
2. In `initiate_build`, instead of using `self.config.static_config.builder_address`, the attacker sets `builder: attacker_address` in the constructed `ProposalInit`.
3. The `ProposalInit` is streamed to all validators as `ProposalPart::Init`.
4. Each validator calls `is_proposal_init_valid` — `builder` is never checked, so validation passes.
5. `initiate_validation` calls `convert_to_sn_api_block_info(init)` → `sequencer_address = attacker_address` → passed to batcher.
6. The blockifier executes all transactions with `sequencer_address = attacker_address`; all fees are credited to the attacker.
7. `PartialBlockHashComponents.sequencer = attacker_address` → `PartialBlockHash` is computed with the attacker's address → `ProposalCommitment` matches the proposer's `ProposalFin.proposal_commitment` → fin-mismatch check passes.
8. 2/3+ validators precommit; the block is decided and committed with `sequencer = attacker_address` in the block header and block hash. [10](#0-9) [11](#0-10) [12](#0-11)

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

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L455-474)
```rust
    let input = ValidateBlockInput {
        proposal_id,
        deadline: clock.now() + chrono_timeout,
        retrospective_block_hash: retrospective_block_hash(
            batcher.clone(),
            state_sync_client,
            init,
            compare_retrospective_block_hash,
        )
        .await
        .map_err(ValidateProposalError::from)?,
        block_info: convert_to_sn_api_block_info(init)?,
    };
    debug!("Initiating validate proposal: input={input:?}");
    batcher.validate_block(input.clone()).await.map_err(|err| {
        ValidateProposalError::Batcher(
            format!("Failed to initiate validate proposal {input:?}."),
            err,
        )
    })?;
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

**File:** crates/apollo_batcher/src/block_builder.rs (L170-194)
```rust
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
```

**File:** crates/starknet_api/src/block_hash/block_hash_calculator.rs (L209-221)
```rust
#[derive(Clone, Debug, Default, PartialEq, Eq, Serialize, Deserialize)]
/// All information required to calculate a block hash except for the state root and the parent
/// block hash.
pub struct PartialBlockHashComponents {
    pub header_commitments: BlockHeaderCommitments,
    pub block_number: BlockNumber,
    pub l1_gas_price: GasPricePerToken,
    pub l1_data_gas_price: GasPricePerToken,
    pub l2_gas_price: GasPricePerToken,
    pub sequencer: SequencerContractAddress,
    pub timestamp: BlockTimestamp,
    pub starknet_version: StarknetVersion,
}
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L397-412)
```rust
        let sequencer = SequencerContractAddress(init.builder);

        let block_header_without_hash = BlockHeaderWithoutHash {
            block_number: height,
            l1_gas_price,
            l1_data_gas_price,
            l2_gas_price,
            l2_gas_consumed: l2_gas_used,
            next_l2_gas_price: self.l2_gas_price,
            sequencer,
            timestamp: BlockTimestamp(init.timestamp),
            l1_da_mode: init.l1_da_mode,
            fee_proposal_fri: init.fee_proposal_fri,
            // TODO(guy.f): Figure out where/if to get the values below from and fill them.
            ..Default::default()
        };
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L806-808)
```rust
            // TODO(Asmaa): Get it from committee once we have it.
            builder_address: self.config.static_config.builder_address,
            cancel_token,
```

**File:** crates/apollo_consensus_orchestrator/src/build_proposal.rs (L169-188)
```rust
    let init = ProposalInit {
        height: args.build_param.height,
        round: args.build_param.round,
        valid_round: args.build_param.valid_round,
        proposer: args.build_param.proposer,
        builder: args.builder_address,
        timestamp,
        l1_da_mode: args.l1_da_mode,
        l2_gas_price_fri: args.l2_gas_price,
        l1_gas_price_wei: l1_prices_wei.l1_gas_price,
        l1_data_gas_price_wei: l1_prices_wei.l1_data_gas_price,
        l1_gas_price_fri: l1_prices_fri.l1_gas_price,
        l1_data_gas_price_fri: l1_prices_fri.l1_data_gas_price,
        starknet_version: starknet_api::block::StarknetVersion::LATEST,
        // TODO(Asmaa): Put the real value once we have it.
        // Sentinel until then; see `expected_version_constant_commitment` for why this is the
        // single source of truth shared with the validator.
        version_constant_commitment: expected_version_constant_commitment(),
        fee_proposal_fri: Some(args.fee_proposal),
    };
```
