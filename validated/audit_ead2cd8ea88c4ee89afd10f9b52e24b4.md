### Title
Unvalidated `ProposalInit.builder` Field Allows Proposer to Commit Arbitrary Sequencer Address into Block Hash - (`crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

### Summary

`ProposalInit.builder` is a proposer-supplied field that flows directly into `sequencer_address` in the committed `BlockInfo`. The validator's `is_proposal_init_valid` function checks every other security-relevant field of `ProposalInit` (height, l1_da_mode, l2_gas_price_fri, timestamp, starknet_version, version_constant_commitment, all four L1 gas prices, fee_proposal_fri) but never checks `builder`. A legitimate-but-malicious proposer can set `builder` to any arbitrary address; all validators accept it, the batcher computes the block hash with that address as `sequencer_address`, and the wrong value is committed to consensus and stored permanently.

### Finding Description

**Step 1 – `builder` enters the system unchecked.**

`ProposalInit` carries a `builder` field described as "Address of the one who builds/sequences the block": [1](#0-0) 

The proposer sets it from a local config value (`args.builder_address`): [2](#0-1) 

**Step 2 – `is_proposal_init_valid` never checks `builder`.**

The entire validation function checks `height`, `l1_da_mode`, `l2_gas_price_fri`, `timestamp`, `starknet_version`, `version_constant_commitment`, four L1 gas prices, and `fee_proposal_fri`. There is no check on `builder`: [3](#0-2) 

**Step 3 – `builder` becomes `sequencer_address` in `BlockInfo`.**

`convert_to_sn_api_block_info` maps `init.builder` directly to `sequencer_address`: [4](#0-3) 

This `BlockInfo` is passed to the batcher via `ValidateBlockInput.block_info` in `initiate_validation`: [5](#0-4) 

**Step 4 – `sequencer_address` is hashed into the committed block hash.**

`PartialBlockHashComponents::new` includes `sequencer_address`: [6](#0-5) 

`calculate_block_hash` chains it into the Poseidon hash: [7](#0-6) 

**Step 5 – Both proposer and validator use the same `init.builder`, so `ProposalFinMismatch` does not fire.**

Because both sides derive `block_info` from the same `ProposalInit`, both compute the same (wrong) block hash. The commitment check at line 244 passes: [8](#0-7) 

**Contrast with `proposer`:** The consensus manager *does* validate `proposer` against the committee-derived expected proposer before calling `validate_proposal`: [9](#0-8) 

No equivalent check exists for `builder`.

### Impact Explanation

A legitimate-but-malicious proposer can set `builder` to any `ContractAddress`. This causes:

1. **Wrong `sequencer_address` committed to the block header** – the stored block header permanently records the attacker-chosen address as the sequencer.
2. **Wrong block hash** – `sequencer_address` is a direct input to the Poseidon block hash; every downstream hash (parent hash of the next block, L1 anchor) is corrupted.
3. **Wrong fee recipient** – the blockifier charges fees and routes them to `sequencer_address`; a malicious proposer can redirect all transaction fees in the block to an address they control.
4. **Wrong `get_sequencer_address()` syscall result** – contracts that call this syscall during execution receive the attacker-chosen address, producing wrong execution results and events.

This matches the allowed impact: *"Wrong state, receipt, event, L1 message, class hash, storage value, or revert result from blockifier/syscall/execution logic for accepted input"* and *"Incorrect fee, gas, bouncer, resource accounting, refund, balance, or L1 gas price effect with economic impact."*

### Likelihood Explanation

The trigger requires the attacker to be the legitimate proposer for a given height/round (enforced by the committee check). This is not an unprivileged external user, but it is a single validator acting within its normal turn. In a permissioned or semi-permissioned validator set this is a realistic threat. The attack requires no special tooling beyond modifying the `builder_address` config or patching the `initiate_build` function locally.

### Recommendation

Add a check inside `is_proposal_init_valid` (or in `ProposalInitValidation`) that enforces `init_proposed.builder == expected_builder_address`, where `expected_builder_address` is derived from the local node's configuration (the same source used by the proposer). This mirrors the existing pattern for `proposer` (validated against the committee) and for `l2_gas_price_fri` (validated against the local config override).

```rust
// In ProposalInitValidation, add:
pub builder_address: ContractAddress,

// In is_proposal_init_valid, add:
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

### Proof of Concept

1. A malicious node is the legitimate proposer for block N, round 0 (passes the committee check in `handle_proposal`).
2. It modifies `initiate_build` to set `builder: ContractAddress::from(ATTACKER_ADDRESS)` instead of `args.builder_address`.
3. It broadcasts the `ProposalInit` with the forged `builder`.
4. Every validator calls `is_proposal_init_valid` — all checks pass because `builder` is never checked.
5. `initiate_validation` calls `convert_to_sn_api_block_info(&init)`, producing a `BlockInfo` with `sequencer_address = ATTACKER_ADDRESS`.
6. The batcher executes the block with `ATTACKER_ADDRESS` as sequencer; all fee transfers go to `ATTACKER_ADDRESS`; `get_sequencer_address()` returns `ATTACKER_ADDRESS`.
7. `PartialBlockHashComponents::new` hashes `ATTACKER_ADDRESS` into the block hash.
8. Both proposer and validator compute the same (wrong) `ProposalCommitment`; `ProposalFinMismatch` does not fire.
9. Consensus reaches decision; the block with wrong sequencer address and wrong block hash is committed to storage.

### Citations

**File:** crates/apollo_protobuf/src/consensus.rs (L106-107)
```rust
    /// Address of the one who builds/sequences the block.
    pub builder: ContractAddress,
```

**File:** crates/apollo_consensus_orchestrator/src/build_proposal.rs (L169-175)
```rust
    let init = ProposalInit {
        height: args.build_param.height,
        round: args.build_param.round,
        valid_round: args.build_param.valid_round,
        proposer: args.build_param.proposer,
        builder: args.builder_address,
        timestamp,
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L243-247)
```rust
    // TODO(matan): Switch to signature validation.
    if built_block != received_fin.proposal_commitment {
        CONSENSUS_PROPOSAL_FIN_MISMATCH.increment(1);
        return Err(ValidateProposalError::ProposalFinMismatch);
    }
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L252-418)
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
    let (l1_gas_prices_fri, l1_gas_prices_wei) = get_l1_prices_in_fri_and_wei(
        l1_gas_price_provider,
        init_proposed.timestamp,
        proposal_init_validation.previous_proposal_init.as_ref(),
        gas_price_params,
    )
    .await;
    let l1_gas_price_margin_percent =
        VersionedConstants::latest_constants().l1_gas_price_margin_percent.into();
    debug!("L1 price info: fri={l1_gas_prices_fri:?}, wei={l1_gas_prices_wei:?}");

    let l1_gas_price_fri = l1_gas_prices_fri.l1_gas_price;
    let l1_data_gas_price_fri = l1_gas_prices_fri.l1_data_gas_price;
    let l1_gas_price_wei = l1_gas_prices_wei.l1_gas_price;
    let l1_data_gas_price_wei = l1_gas_prices_wei.l1_data_gas_price;
    let l1_gas_price_fri_proposed = init_proposed.l1_gas_price_fri;
    let l1_data_gas_price_fri_proposed = init_proposed.l1_data_gas_price_fri;
    let l1_gas_price_wei_proposed = init_proposed.l1_gas_price_wei;
    let l1_data_gas_price_wei_proposed = init_proposed.l1_data_gas_price_wei;

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

    // fee_proposal is required iff Starknet version >= V0_14_3.
    let fee_proposal_required = init_proposed.starknet_version >= StarknetVersion::V0_14_3;
    match (init_proposed.fee_proposal_fri, fee_proposal_required) {
        (Some(_), false) => {
            return Err(ValidateProposalError::InvalidProposalInit(
                init_proposed.clone(),
                proposal_init_validation.clone(),
                format!(
                    "fee_proposal must be absent before V0_14_3, got Some at version {}",
                    init_proposed.starknet_version
                ),
            ));
        }
        (None, true) => {
            return Err(ValidateProposalError::InvalidProposalInit(
                init_proposed.clone(),
                proposal_init_validation.clone(),
                format!(
                    "fee_proposal is required at V0_14_3+, got None at version {}",
                    init_proposed.starknet_version
                ),
            ));
        }
        _ => {}
    }

    // Validate fee_proposal is within the configured margin of fee_actual.
    // During initiation (fee_actual is None, <window_size blocks), bounds are not enforced.
    if let (Some(fee_actual), Some(fee_proposal)) =
        (proposal_init_validation.fee_actual, init_proposed.fee_proposal_fri)
    {
        let (lower_bound, upper_bound) = fee_proposal_bounds(
            fee_actual,
            VersionedConstants::latest_constants().fee_proposal_margin_ppt,
        );
        if fee_proposal.0 < lower_bound || fee_proposal.0 > upper_bound {
            return Err(ValidateProposalError::InvalidProposalInit(
                init_proposed.clone(),
                proposal_init_validation.clone(),
                format!(
                    "Fee proposal out of bounds: fee_actual={}, fee_proposal={}, allowed \
                     range=[{lower_bound}, {upper_bound}]",
                    fee_actual.0, fee_proposal.0
                ),
            ));
        }
    }

    Ok(())
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L455-467)
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
```

**File:** crates/apollo_consensus_orchestrator/src/utils.rs (L329-333)
```rust
    Ok(starknet_api::block::BlockInfo {
        block_number: init.height,
        block_timestamp: BlockTimestamp(init.timestamp),
        sequencer_address: init.builder,
        gas_prices: GasPrices {
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
