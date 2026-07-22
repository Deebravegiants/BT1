### Title
`ProposalInit.builder` (sequencer address) is not validated in `is_proposal_init_valid`, allowing a malicious proposer to inject an arbitrary sequencer address into the executed block context and block hash — (`crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

### Summary

`is_proposal_init_valid` validates `height`, `l1_da_mode`, `l2_gas_price_fri`, all four L1 gas prices, `starknet_version`, `version_constant_commitment`, `fee_proposal_fri`, and `timestamp`, but it never checks `ProposalInit.builder`. The `builder` field is the sequencer address that is passed verbatim into the block context and into `PartialBlockHashComponents.sequencer`, which is a direct input to the block hash. A malicious proposer can set `builder` to any arbitrary address; every validating node will accept the proposal, execute all transactions with the wrong `sequencer_address` in the block context, and commit a block whose hash encodes the attacker-chosen address.

### Finding Description

`ProposalInit` carries a `builder` field (the sequencer/block-builder address). [1](#0-0) 

During proposal validation, `is_proposal_init_valid` is called to check the proposer-supplied metadata against locally-derived reference values. [2](#0-1) 

The function checks `height`, `l1_da_mode`, `l2_gas_price_fri`, all four L1 gas prices (within a margin), `starknet_version`, `version_constant_commitment`, `fee_proposal_fri`, and `timestamp`. [3](#0-2) 

`ProposalInitValidation` — the struct that carries the locally-trusted reference values — has no `builder` or `sequencer_address` field at all. [4](#0-3) 

After `is_proposal_init_valid` passes, `initiate_validation` converts the accepted `ProposalInit` into a `BlockInfo` via `convert_to_sn_api_block_info`, which maps `init.builder` directly to `sequencer_address`. [5](#0-4) 

That `BlockInfo` is forwarded to the batcher as `ValidateBlockInput.block_info`, so every transaction in the proposal is executed with the attacker-chosen `sequencer_address` in the block context. [6](#0-5) 

`sequencer_address` is then captured in `PartialBlockHashComponents.sequencer` and hashed into the `PartialBlockHash` / `ProposalCommitment`. [7](#0-6) [8](#0-7) 

Because the batcher computes its own `ProposalCommitment` from the same (attacker-supplied) `builder`, the `built_block != received_fin.proposal_commitment` guard does not fire — both sides agree on the wrong hash. [9](#0-8) 

### Impact Explanation

Three concrete harms follow from an unchecked `builder`:

1. **Wrong block hash committed to L1.** `sequencer_address` is a direct input to `calculate_block_hash`. A forged `builder` produces a block hash that encodes the attacker's address, permanently corrupting the L1 anchor for that height.

2. **Wrong execution context for all transactions.** Any contract that calls `get_execution_info().block_info.sequencer_address` (e.g., to gate sequencer-only logic or to compute fee rebates) receives the attacker-chosen value. This is a wrong execution result from blockifier/syscall logic for accepted input — Critical per the allowed impact scope.

3. **Sequencer fee misdirection.** Fees collected to `sequencer_address` during block execution flow to the attacker-controlled address rather than the legitimate sequencer.

### Likelihood Explanation

The trigger requires a node that is a member of the active proposer set to send a `ProposalInit` with a crafted `builder`. In a Tendermint BFT sequencer set this is a Byzantine-fault scenario (one of `f` faulty nodes), which is exactly the threat model that proposal validation is designed to defend against. No external, unpermissioned actor is needed; any single compromised or malicious sequencer node suffices.

### Recommendation

Add `builder` (and optionally `proposer`) to `ProposalInitValidation` and check it in `is_proposal_init_valid`, analogously to how `l2_gas_price_fri` and `l1_da_mode` are checked:

```rust
// In ProposalInitValidation:
pub builder: ContractAddress,

// In is_proposal_init_valid:
if init_proposed.builder != proposal_init_validation.builder {
    return Err(ValidateProposalError::InvalidProposalInit(
        init_proposed.clone(),
        proposal_init_validation.clone(),
        format!(
            "builder mismatch: expected={:?}, proposed={:?}",
            proposal_init_validation.builder, init_proposed.builder
        ),
    ));
}
```

The validator's own `builder_address` (already used when building proposals) should be the reference value. [10](#0-9) 

### Proof of Concept

1. Malicious sequencer node M is selected as proposer for height H.
2. M constructs `ProposalInit { builder: attacker_address, ... }` with all other fields (gas prices, timestamp, etc.) within the accepted margins.
3. M streams the proposal to all validators.
4. Each validator calls `is_proposal_init_valid` — no check on `builder` exists, so validation passes.
5. `initiate_validation` calls `convert_to_sn_api_block_info(&init)`, producing `BlockInfo { sequencer_address: attacker_address, ... }`.
6. The batcher executes all transactions with `sequencer_address = attacker_address` in the block context.
7. `PartialBlockHashComponents::new` captures `attacker_address` as `sequencer`.
8. `PartialBlockHash::from_partial_block_hash_components` produces a commitment that encodes `attacker_address`.
9. The batcher's commitment matches M's `ProposalFin.proposal_commitment` (both computed from the same forged `builder`), so `ProposalFinMismatch` is not triggered.
10. Consensus reaches decision; the block with `sequencer_address = attacker_address` is committed to storage and its hash is anchored to L1. [11](#0-10) [12](#0-11) [13](#0-12)

### Citations

**File:** crates/apollo_protobuf/src/consensus.rs (L107-107)
```rust
    pub builder: ContractAddress,
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L74-85)
```rust
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

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L153-160)
```rust
    is_proposal_init_valid(
        &args.proposal_init_validation,
        &args.init,
        args.deps.clock.as_ref(),
        args.deps.l1_gas_price_provider,
        &args.gas_price_params,
    )
    .await?;
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L244-247)
```rust
    if built_block != received_fin.proposal_commitment {
        CONSENSUS_PROPOSAL_FIN_MISMATCH.increment(1);
        return Err(ValidateProposalError::ProposalFinMismatch);
    }
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L252-320)
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
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L455-475)
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
    Ok(())
```

**File:** crates/apollo_consensus_orchestrator/src/utils.rs (L301-348)
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
}
```

**File:** crates/starknet_api/src/block_hash/block_hash_calculator.rs (L197-206)
```rust
    pub fn from_partial_block_hash_components(
        partial_block_hash_components: &PartialBlockHashComponents,
    ) -> StarknetApiResult<Self> {
        let block_hash = calculate_block_hash(
            partial_block_hash_components,
            Self::GLOBAL_ROOT_FOR_PARTIAL_BLOCK_HASH,
            Self::PARENT_HASH_FOR_PARTIAL_BLOCK_HASH,
        )?;
        Ok(Self(block_hash.0))
    }
```

**File:** crates/starknet_api/src/block_hash/block_hash_calculator.rs (L224-235)
```rust
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

**File:** crates/starknet_api/src/block_hash/block_hash_calculator.rs (L253-260)
```rust
    Ok(BlockHash(
        HashChain::new()
            .chain(&block_hash_version.clone().into())
            .chain(&partial_block_hash_components.block_number.0.into())
            .chain(&state_root.0)
            .chain(&partial_block_hash_components.sequencer.0)
            .chain(&partial_block_hash_components.timestamp.0.into())
            .chain(&block_commitments.concatenated_counts)
```

**File:** crates/apollo_consensus_orchestrator/src/build_proposal.rs (L174-174)
```rust
        builder: args.builder_address,
```
