### Title
`ProposalInit.builder` Accepted Without Validation Against Locally-Configured `builder_address`, Corrupting `sequencer_address` in Block Hash and Execution Context — (`File: crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

### Summary

`is_proposal_init_valid` validates many fields of a received `ProposalInit` (height, L1/L2 gas prices, `l1_da_mode`, `starknet_version`, `version_constant_commitment`, `fee_proposal_fri`) but never checks `init.builder` against the locally-configured `ContextStaticConfig::builder_address`. The `builder` field is passed verbatim to `convert_to_sn_api_block_info`, which maps it to `sequencer_address` in `BlockInfo`. That `BlockInfo` is forwarded to the batcher for block execution and is also used to compute `PartialBlockHashComponents` (and therefore the `PartialBlockHash` / `ProposalCommitment`). A legitimate consensus proposer can set `init.builder` to any arbitrary address; every validator node will accept the proposal, execute all transactions with the attacker-chosen `sequencer_address`, and commit a block whose hash encodes the wrong sequencer.

### Finding Description

**The unvalidated field:**

`ProposalInit` carries a `builder: ContractAddress` field — "Address of the one who builds/sequences the block." [1](#0-0) 

The honest proposer sets it from config: [2](#0-1) 

**The missing check in `is_proposal_init_valid`:**

The function checks `height`, `l1_da_mode`, `l2_gas_price_fri`, `starknet_version`, `version_constant_commitment`, all four L1 gas price fields, and `fee_proposal_fri`. It never checks `init.builder`: [3](#0-2) 

`ProposalInitValidation` — the struct that carries the locally-trusted reference values — has no `builder_address` field at all: [4](#0-3) 

**How `builder` reaches execution and the block hash:**

After `is_proposal_init_valid` passes, `initiate_validation` calls `convert_to_sn_api_block_info(init)`, which maps `init.builder` directly to `sequencer_address`: [5](#0-4) 

The resulting `BlockInfo` is sent to the batcher as `ValidateBlockInput.block_info`. Inside the batcher, `BlockExecutionArtifacts::new` calls `PartialBlockHashComponents::new(&block_info, header_commitments)`: [6](#0-5) 

`PartialBlockHashComponents::new` stores `sequencer_address` as the `sequencer` field: [7](#0-6) 

`calculate_block_hash` chains `sequencer` into the Poseidon hash: [8](#0-7) 

**The `builder_address` config is never consulted during validation:**

The validator node has `config.static_config.builder_address` (a `ContractAddress` set at startup): [9](#0-8) 

This value is used only when the node itself builds a proposal. It is never placed into `ProposalInitValidation` and never compared against `init.builder` during validation.

### Impact Explanation

**Wrong block hash / state commitment (Critical):** The `sequencer` field is a direct input to `calculate_block_hash`. A proposer-controlled `builder` value produces a `PartialBlockHash` — and therefore a `ProposalCommitment` — that encodes the wrong sequencer address. Every validator that accepts the proposal computes the same wrong commitment (because they all use the proposer-supplied `init.builder`), so consensus reaches agreement on a block with a corrupted hash.

**Wrong execution result from `get_execution_info` syscall (Critical):** During transaction execution the batcher uses the `BlockInfo` derived from `init.builder` as `sequencer_address`. Any contract that calls `get_execution_info().block_info.sequencer_address` receives the attacker-chosen address. Fee-collection logic, access-control checks, and any contract that branches on the sequencer address will behave incorrectly.

**Wrong fee accounting (Critical):** The sequencer address is the recipient of transaction fees in the Starknet fee model. Redirecting it to an attacker-controlled address diverts fee revenue.

### Likelihood Explanation

The trigger requires a legitimate consensus proposer (one whose `proposer` address is selected by the committee for the current height/round). The `proposer` field is validated against the committee: [10](#0-9) 

However, `builder` is a separate field that is never checked. In the current single-sequencer deployment all validators share the same `builder_address` config value, so any proposer node that deviates (maliciously or due to misconfiguration) can set `builder` to an arbitrary address. No special privilege beyond being the scheduled proposer is required.

### Recommendation

Add `builder_address: ContractAddress` to `ProposalInitValidation` and check it in `is_proposal_init_valid`:

```rust
// In ProposalInitValidation:
pub builder_address: ContractAddress,

// In is_proposal_init_valid, after the existing height/l1_da_mode/l2_gas_price check:
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

Populate `builder_address` from `self.config.static_config.builder_address` when constructing `ProposalInitValidation` in both `validate_proposal` call sites in `sequencer_consensus_context.rs`. [11](#0-10) 

### Proof of Concept

```rust
// In a test that exercises validate_proposal:
// 1. Create a proposal_args with a valid init (all gas prices, height, etc. correct).
// 2. Mutate init.builder to an attacker-controlled address:
proposal_args.init.builder = ContractAddress::from(0xdeadbeef_u64);

// 3. Run validate_proposal — it succeeds (no builder check):
let res = validate_proposal(proposal_args.into()).await;
assert!(res.is_ok(), "Expected Ok but got: {res:?}");

// 4. Inspect the BlockInfo sent to the batcher via validate_block:
// The batcher receives sequencer_address = 0xdeadbeef, not the configured builder_address.
// PartialBlockHashComponents.sequencer = 0xdeadbeef.
// calculate_block_hash produces a hash that encodes the wrong sequencer.
// Any contract calling get_execution_info().block_info.sequencer_address
// returns 0xdeadbeef instead of the legitimate sequencer address.
```

The existing test infrastructure in `validate_proposal_test.rs` already demonstrates that mutating a single `init` field (e.g. `l2_gas_price_fri`) causes rejection. The same test pattern applied to `init.builder` shows acceptance — confirming the missing guard. [12](#0-11)

### Citations

**File:** crates/apollo_protobuf/src/consensus.rs (L106-108)
```rust
    /// Address of the one who builds/sequences the block.
    pub builder: ContractAddress,
    /// L1 data availability mode.
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

**File:** crates/apollo_batcher/src/block_builder.rs (L178-179)
```rust
        let partial_block_hash_components =
            PartialBlockHashComponents::new(&block_info, header_commitments);
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

**File:** crates/starknet_api/src/block_hash/block_hash_calculator.rs (L253-282)
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
}
```

**File:** crates/apollo_consensus_orchestrator_config/src/config.rs (L163-165)
```rust
    pub l1_da_mode: bool,
    /// The address of the contract that builds the block.
    pub builder_address: ContractAddress,
```

**File:** crates/apollo_consensus/src/manager.rs (L849-866)
```rust
                let Ok(proposer) =
                    get_proposer_for_height(&self.committee_provider, init.height, init.round)
                        .await
                else {
                    warn!(
                        "VIRTUAL_PROPOSER_LOOKUP_FAILED: Failed to determine virtual proposer for \
                         height {} round {}. Dropping proposal.",
                        init.height.0, init.round
                    );
                    return Ok(VecDeque::new());
                };
                if proposer != init.proposer {
                    warn!(
                        "Invalid proposer for height {} and round {}: expected {:?}, got {:?}",
                        init.height.0, init.round, proposer, init.proposer
                    );
                    return Ok(VecDeque::new());
                }
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L878-910)
```rust
            }
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
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal_test.rs (L290-300)
```rust
#[tokio::test]
async fn invalid_proposal_init() {
    let (mut proposal_args, mut content_sender) = create_proposal_validate_arguments();

    proposal_args.init.l2_gas_price_fri =
        GasPrice(proposal_args.proposal_init_validation.l2_gas_price_fri.0 + 1);
    content_sender.send(ProposalPart::Init(proposal_args.init.clone())).await.unwrap();

    let res = validate_proposal(proposal_args.into()).await;
    assert!(matches!(res, Err(ValidateProposalError::InvalidProposalInit(_, _, _))));
}
```
