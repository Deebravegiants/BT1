### Title
Unvalidated `ProposalInit.builder` Field Allows Malicious Proposer to Corrupt Sequencer Address in Block Hash and Fee Collection - (File: crates/apollo_consensus_orchestrator/src/validate_proposal.rs)

### Summary

`ProposalInit.builder` is accepted verbatim from the network, mapped directly to `sequencer_address` in `BlockInfo`, and committed into the `PartialBlockHash`. The `is_proposal_init_valid` function and the `ProposalInitValidation` struct contain no check for this field. A malicious proposer can set `builder` to any address, causing validators to execute and finalize a block with an attacker-controlled sequencer address, corrupting both fee collection and the canonical block hash.

### Finding Description

`ProposalInit` carries a `builder` field ("Address of the one who builds/sequences the block"). In `convert_to_sn_api_block_info`, this field is mapped directly to `sequencer_address` in the `BlockInfo` that is passed to the batcher:

```rust
// crates/apollo_consensus_orchestrator/src/utils.rs:329-347
Ok(starknet_api::block::BlockInfo {
    block_number: init.height,
    block_timestamp: BlockTimestamp(init.timestamp),
    sequencer_address: init.builder,   // ← proposer-supplied, never validated
    gas_prices: GasPrices { ... },
    ...
})
``` [1](#0-0) 

This `BlockInfo` is used in both the build path (`initiate_build` → `propose_block`) and the validate path (`initiate_validation` → `validate_block`): [2](#0-1) 

The `sequencer_address` then flows into `PartialBlockHashComponents::new`, which commits it into the `PartialBlockHash` / `ProposalCommitment`: [3](#0-2) 

The `calculate_block_hash` function chains the sequencer address directly into the Poseidon hash: [4](#0-3) 

The `ProposalInitValidation` struct — the sole source of locally-trusted reference values used by `is_proposal_init_valid` — has no `builder` field: [5](#0-4) 

`is_proposal_init_valid` validates `height`, `l1_da_mode`, `l2_gas_price_fri`, `starknet_version`, `version_constant_commitment`, all four L1 gas prices, and `fee_proposal_fri` — but never `init_proposed.builder`: [6](#0-5) 

The proposer sets `builder` from its own config (`args.builder_address`): [7](#0-6) 

No other code in the validation path checks `init.builder` against an expected value. The grep confirms only two sites reference `init.builder` — the proposer's construction and the `convert_to_sn_api_block_info` mapping — neither of which is a validation.

### Impact Explanation

**Wrong block hash committed to consensus.** The `sequencer_address` is a direct input to `calculate_block_hash`. A proposer that sets `init.builder = attacker_address` causes every validating node to compute a `PartialBlockHash` over the attacker's address. The proposer sends a matching `ProposalFin.proposal_commitment` (computed from the same attacker-controlled `builder`). The validator's only commitment check is `built_block != received_fin.proposal_commitment`, which passes because both sides used the same attacker-supplied `builder`. The block is finalized with a wrong, attacker-controlled sequencer address baked into the canonical block hash.

**Wrong fee recipient.** The blockifier uses `sequencer_address` from `BlockInfo` as the fee recipient for all transactions in the block. With `builder` set to an attacker address, all transaction fees in the block are credited to the attacker instead of the legitimate sequencer.

This matches the impact category: *Wrong state, receipt, event, L1 message, class hash, storage value, or revert result from blockifier/syscall/execution logic for accepted input* and *Incorrect fee, gas, bouncer, resource accounting, refund, balance, or L1 gas price effect with economic impact.*

### Likelihood Explanation

Any node that wins the proposer election for a round can exploit this. The trigger is a single field in `ProposalInit` sent over the consensus P2P channel. No special privilege beyond being the elected proposer is required. The attack is silent — validators accept the proposal normally and the corrupted block hash propagates to all nodes.

### Recommendation

Add `builder` to `ProposalInitValidation` and check it in `is_proposal_init_valid`, analogously to how `l1_da_mode` and `l2_gas_price_fri` are checked:

```rust
// In ProposalInitValidation:
pub expected_builder: ContractAddress,

// In is_proposal_init_valid:
if init_proposed.builder != proposal_init_validation.expected_builder {
    return Err(ValidateProposalError::InvalidProposalInit(
        init_proposed.clone(),
        proposal_init_validation.clone(),
        format!(
            "builder mismatch: expected={:?}, proposed={:?}",
            proposal_init_validation.expected_builder, init_proposed.builder
        ),
    ));
}
```

The `expected_builder` value should be sourced from the same locally-trusted config field (`static_config.builder_address`) used by the proposer, populated in `validate_proposal` inside `SequencerConsensusContext` alongside the other `ProposalInitValidation` fields. [8](#0-7) 

### Proof of Concept

1. Attacker wins proposer election for height H, round R.
2. In `initiate_build`, attacker sets `builder: attacker_controlled_address` instead of `args.builder_address`.
3. `convert_to_sn_api_block_info` maps this to `sequencer_address: attacker_controlled_address` and passes it to `propose_block`.
4. The batcher executes the block with `sequencer_address = attacker_controlled_address`; all transaction fees are credited to the attacker.
5. `PartialBlockHashComponents::new` commits `attacker_controlled_address` as the sequencer into the partial block hash.
6. Attacker sends `ProposalFin { proposal_commitment: commitment_over_attacker_address, ... }`.
7. Each validating node calls `is_proposal_init_valid` — no check on `builder` — then `initiate_validation` → `convert_to_sn_api_block_info(init)` → batcher executes with `sequencer_address = attacker_controlled_address` → computes the same commitment.
8. `built_block == received_fin.proposal_commitment` passes; the proposal is accepted.
9. `decision_reached` finalizes the block. The canonical block hash contains the attacker's address as sequencer; all fees for the block are in the attacker's account.

### Citations

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

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L879-912)
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
                self.validate_current_round_proposal(
                    init,
                    proposal_init_validation,
                    timeout,
                    self.config.static_config.validate_proposal_margin_millis,
                    content_receiver,
                    fin_sender,
                )
                .await;
                fin_receiver
            }
        }
```
