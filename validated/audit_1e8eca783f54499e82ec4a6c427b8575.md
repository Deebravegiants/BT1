### Title
`ProposalInit.builder` Is Never Validated by the Validator Node, Allowing a Malicious Proposer to Inject an Arbitrary Sequencer Address into Block Hash and Execution Context — (`crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

### Summary

`is_proposal_init_valid` enforces every security-sensitive field of `ProposalInit` (height, l1_da_mode, l2_gas_price_fri, starknet_version, version_constant_commitment, all four L1 gas prices, fee_proposal_fri, timestamp) but silently omits the `builder` field. `builder` is passed verbatim to `convert_to_sn_api_block_info` as `sequencer_address`, which flows into both the execution `BlockInfo` (affecting the `get_sequencer_address` syscall) and `PartialBlockHashComponents.sequencer` (affecting the committed block hash). A malicious proposer can set `builder` to any address; every validator will accept the proposal and commit a block with the wrong sequencer address.

### Finding Description

`ProposalInit` carries a `builder` field that identifies the block-building node: [1](#0-0) 

`is_proposal_init_valid` validates the following fields against locally-trusted reference values: [2](#0-1) [3](#0-2) [4](#0-3) 

`builder` is absent from `ProposalInitValidation` entirely: [5](#0-4) 

After `is_proposal_init_valid` returns `Ok`, `initiate_validation` calls `convert_to_sn_api_block_info`, which maps `init.builder` directly to `sequencer_address`: [6](#0-5) 

`sequencer_address` is then embedded in `PartialBlockHashComponents`: [7](#0-6) 

and hashed into the committed block hash: [8](#0-7) 

By contrast, `proposer` is validated at the consensus layer before `validate_proposal` is ever called: [9](#0-8) 

`builder` receives no equivalent check anywhere in the validation pipeline.

### Impact Explanation

A malicious proposer sets `init.builder` to an arbitrary address `X`. Every validator node calls `is_proposal_init_valid`, which does not inspect `builder`, so the proposal passes. `convert_to_sn_api_block_info` sets `sequencer_address = X` in `BlockInfo`. This produces two concrete corruptions:

1. **Wrong syscall result**: every contract that calls `get_sequencer_address` during execution of this block receives `X` instead of the legitimate sequencer address. Contracts that use this for access control or fee routing behave incorrectly.
2. **Wrong block hash**: `PartialBlockHashComponents.sequencer = X` is hashed into the `PartialBlockHash` / `ProposalCommitment`. The committed block hash differs from what honest nodes would compute with the correct builder address. Because all validators use the proposer-supplied `builder`, they all converge on the same wrong hash, so consensus succeeds on a corrupted value.

Both effects match the allowed impact scope: wrong execution/syscall result and wrong block hash commitment.

### Likelihood Explanation

The trigger requires being the designated proposer for a consensus round. In BFT consensus any validator node can be selected as proposer in rotation. A single Byzantine validator among the committee can exploit this every time it is selected as proposer, without any additional privilege beyond normal protocol participation.

### Recommendation

Add `builder` to `ProposalInitValidation` and check it inside `is_proposal_init_valid`. The validator node knows its own expected builder address (the same value used in `build_proposal` via `args.builder_address`). The check should be an exact equality:

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

This mirrors the pattern already applied to `l1_da_mode`, `l2_gas_price_fri`, and `starknet_version`.

### Proof of Concept

1. A Byzantine validator is selected as proposer for height H, round R.
2. It constructs `ProposalInit` with `builder = <attacker_address>` instead of the legitimate sequencer address.
3. It streams the proposal to all validators.
4. Each validator calls `validate_proposal` → `is_proposal_init_valid`. The function checks height, l1_da_mode, l2_gas_price_fri, starknet_version, version_constant_commitment, L1 gas prices, fee_proposal_fri — but not `builder`. Returns `Ok`.
5. `initiate_validation` calls `convert_to_sn_api_block_info(init)`, producing `BlockInfo { sequencer_address: <attacker_address>, … }`.
6. The batcher executes all transactions with `sequencer_address = <attacker_address>`. Every `get_sequencer_address` syscall returns `<attacker_address>`.
7. `BlockExecutionArtifacts::new` calls `PartialBlockHashComponents::new(&block_info, …)`, embedding `<attacker_address>` as `sequencer`.
8. `PartialBlockHash::from_partial_block_hash_components` hashes this into the commitment. The `ProposalFin` carries this commitment; the validator's locally-computed commitment matches (both used `<attacker_address>`), so `ProposalFinMismatch` is not triggered.
9. Consensus reaches decision on a block whose hash encodes the wrong sequencer address and whose execution results are corrupted. [10](#0-9) [11](#0-10) [12](#0-11)

### Citations

**File:** crates/apollo_protobuf/src/consensus.rs (L107-107)
```rust
    pub builder: ContractAddress,
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L75-85)
```rust
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

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L141-171)
```rust
pub(crate) async fn validate_proposal(
    mut args: ProposalValidateArguments,
) -> ValidateProposalResult<ProposalCommitment> {
    let mut content = Vec::new();
    let mut verify_and_store_proof_tasks: Vec<VerifyAndStoreProofTask> = Vec::new();
    let now = args.deps.clock.now();

    let Some(deadline) = now.checked_add_signed(chrono::TimeDelta::from_std(args.timeout).unwrap())
    else {
        return Err(ValidateProposalError::CannotCalculateDeadline { timeout: args.timeout, now });
    };

    is_proposal_init_valid(
        &args.proposal_init_validation,
        &args.init,
        args.deps.clock.as_ref(),
        args.deps.l1_gas_price_provider,
        &args.gas_price_params,
    )
    .await?;

    initiate_validation(
        args.deps.batcher.clone(),
        args.deps.state_sync_client,
        &args.init,
        args.proposal_id,
        args.timeout + args.batcher_timeout_margin,
        args.deps.clock.as_ref(),
        args.compare_retrospective_block_hash,
    )
    .await?;
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L286-295)
```rust
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

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L342-368)
```rust
    if !(within_margin(l1_gas_price_fri_proposed, l1_gas_price_fri, l1_gas_price_margin_percent)
        && within_margin(
            l1_data_gas_price_fri_proposed,
            l1_data_gas_price_fri,
            l1_gas_price_margin_percent,
        )
        && within_margin(l1_gas_price_wei_proposed, l1_gas_price_wei, l1_gas_price_margin_percent)
        && within_margin(
            l1_data_gas_price_wei_proposed,
            l1_data_gas_price_wei,
            l1_gas_price_margin_percent,
        ))
    {
        return Err(ValidateProposalError::InvalidProposalInit(
            init_proposed.clone(),
            proposal_init_validation.clone(),
            format!(
                "L1 gas price mismatch: expected L1 gas price FRI={l1_gas_price_fri}, \
                 proposed={l1_gas_price_fri_proposed}, expected L1 data gas price \
                 FRI={l1_data_gas_price_fri}, proposed={l1_data_gas_price_fri_proposed}, expected \
                 L1 gas price WEI={l1_gas_price_wei}, proposed={l1_gas_price_wei_proposed}, \
                 expected L1 data gas price WEI={l1_data_gas_price_wei}, \
                 proposed={l1_data_gas_price_wei_proposed}, \
                 l1_gas_price_margin_percent={l1_gas_price_margin_percent}"
            ),
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

**File:** crates/starknet_api/src/block_hash/block_hash_calculator.rs (L209-235)
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

**File:** crates/apollo_consensus/src/single_height_consensus.rs (L114-120)
```rust
        let Ok(proposer_id) = self.committee.get_proposer(height, init.round) else {
            return VecDeque::new();
        };
        if init.proposer != proposer_id {
            warn!("Invalid proposer: expected {:?}, got {:?}", proposer_id, init.proposer);
            return VecDeque::new();
        }
```

**File:** crates/apollo_batcher/src/block_builder.rs (L166-194)
```rust
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
```
